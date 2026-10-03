# eval_utils.py

import os
import time
import random

import numpy as np
import torch
from torch.utils.data import DataLoader, Subset

from config import (
    TRAIN_IMAGES_DIR,
    TRAIN_MASKS_DIR,
    TEST_IMAGES_DIR,
    TEST_MASKS_DIR,
    NUM_CLASSES,
    DEVICE,
)
from dataset import CholecSegDataset
from model import compute_iou


def calculate_fps(wrapper, batch_size: int = 1) -> float:
    """
    Measure average FPS on the entire test split.
    """
    # Load latest checkpoint
    ckpt = wrapper.load_latest()
    print(f"Loaded checkpoint for FPS eval: {ckpt}")

    # Prepare test dataset & loader
    image_paths = sorted(
        os.path.join(TEST_IMAGES_DIR, fname)
        for fname in os.listdir(TEST_IMAGES_DIR)
        if fname.lower().endswith(".png")
    )
    mask_paths = sorted(
        os.path.join(TEST_MASKS_DIR, fname)
        for fname in os.listdir(TEST_MASKS_DIR)
        if fname.lower().endswith(".png")
    )
    ds = CholecSegDataset(image_paths, mask_paths)
    dl = DataLoader(ds, batch_size=batch_size, shuffle=False, pin_memory=True)

    # Warm-up (one batch)
    wrapper.model.eval()
    imgs, _ = next(iter(dl))
    with torch.no_grad():
        _ = wrapper.predict(imgs.to(DEVICE))

    # Timed runs over entire test set
    start = time.time()
    count = 0
    with torch.no_grad():
        for imgs, _ in dl:
            imgs = imgs.to(DEVICE)
            _ = wrapper.predict(imgs)
            count += imgs.shape[0]

    elapsed = time.time() - start
    fps = count / elapsed if elapsed > 0 else 0.0
    print(f"Processed {count} samples in {elapsed:.2f}s → FPS: {fps:.2f}")
    return fps


def evaluate_miou(wrapper, batch_size: int = 1) -> float:
    """
    Compute final mean IoU over the entire train split.
    """
    # Load latest checkpoint
    ckpt = wrapper.load_latest()
    print(f"Loaded checkpoint for mIoU eval: {ckpt}")

    # Prepare train dataset & loader
    image_paths = sorted(
        os.path.join(TRAIN_IMAGES_DIR, fname)
        for fname in os.listdir(TRAIN_IMAGES_DIR)
        if fname.lower().endswith(".png")
    )
    mask_paths = sorted(
        os.path.join(TRAIN_MASKS_DIR, fname)
        for fname in os.listdir(TRAIN_MASKS_DIR)
        if fname.lower().endswith(".png")
    )
    ds = CholecSegDataset(image_paths, mask_paths)
    dl = DataLoader(ds, batch_size=batch_size, shuffle=False, pin_memory=True)

    iou_list = []
    wrapper.model.eval()
    with torch.no_grad():
        for imgs, masks in dl:
            imgs, masks = imgs.to(DEVICE), masks.to(DEVICE)
            logits = wrapper.predict(imgs)
            preds = logits.argmax(dim=1)
            for p, m in zip(preds, masks):
                iou_list.append(
                    float(np.nanmean(compute_iou(p.cpu(), m.cpu(), NUM_CLASSES)))
                )

    mean_iou = float(np.nanmean(iou_list))
    print(f"Mean IoU over {len(iou_list)} train samples: {mean_iou:.4f}")
    return mean_iou
