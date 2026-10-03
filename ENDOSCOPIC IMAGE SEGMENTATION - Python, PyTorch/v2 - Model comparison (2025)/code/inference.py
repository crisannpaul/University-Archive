# inference.py

import os
import random
import numpy as np
import torch
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader

from config import (
    TEST_IMAGES_DIR,
    TEST_MASKS_DIR,
    NUM_CLASSES,
    DEVICE,
    PLOT_PATH
)
from dataset import CholecSegDataset
from model import ModelWrapper, compute_iou, denormalize


def inference(wrapper: ModelWrapper, filenames=None, batch_size: int = 1):
    """
    Universal inference function for any segmentation model wrapped by ModelWrapper.
    If 'filenames' is provided and non‐empty, run inference on those specific test images;
    otherwise pick a random test sample.
    """
    # if filenames is None:
    #     filenames = []
    # filenames.append("frame_513_endo.png")
    # filenames.append("frame_20042_endo.png")

    # 1) Load the latest checkpoint
    checkpoint = wrapper.load_latest()
    print(f"Loaded checkpoint: {checkpoint}")

    # 2) Prepare test dataset
    image_paths = sorted([
        os.path.join(TEST_IMAGES_DIR, fname)
        for fname in os.listdir(TEST_IMAGES_DIR)
        if fname.lower().endswith(".png")
    ])
    mask_paths = sorted([
        os.path.join(TEST_MASKS_DIR, fname)
        for fname in os.listdir(TEST_MASKS_DIR)
        if fname.lower().endswith(".png")
    ])
    ds = CholecSegDataset(image_paths, mask_paths)
    dl = DataLoader(ds, batch_size=batch_size, shuffle=False, pin_memory=True)

    # 3) Determine indices to run inference on
    if filenames:
        # Map each requested filename to its dataset index
        indices = []
        for fn in filenames:
            # Ensure exact match of base filename
            matches = [i for i, path in enumerate(image_paths)
                       if os.path.basename(path) == fn]
            if not matches:
                print(f"Warning: '{fn}' not found in test set, skipping.")
            else:
                indices.extend(matches)
        if not indices:
            # fallback to random if none matched
            idx_list = [random.randrange(len(ds))]
        else:
            idx_list = indices
    else:
        # pick exactly one random index
        idx_list = [random.randrange(len(ds))]

    # 4) For each chosen index, run inference & save a separate plot
    for idx in idx_list:
        img_t, mask_t = ds[idx]

        # Forward pass
        wrapper.model.eval()
        with torch.no_grad():
            raw = wrapper.model(img_t.unsqueeze(0).to(DEVICE))
            out = raw["out"] if isinstance(raw, dict) else raw
            pred = out.argmax(dim=1).squeeze(0).cpu()

        # Compute IoU
        per_class_iou = compute_iou(pred, mask_t, NUM_CLASSES)
        iou_score = float(np.nanmean(per_class_iou))
        print(f"Image '{os.path.basename(image_paths[idx])}' IoU: {iou_score:.4f}")

        # Denormalize + mismatch
        img_np = denormalize(img_t, ds.mean, ds.std)
        gt_mask = mask_t.cpu().numpy()
        mismatch = (pred.numpy() != gt_mask)

        # Plot 4-panel figure
        fig, axes = plt.subplots(1, 4, figsize=(16, 4))
        axes[0].imshow(img_np)
        axes[0].set_title("Input")
        axes[0].axis("off")

        axes[1].imshow(gt_mask, cmap="gray")
        axes[1].set_title("Ground Truth")
        axes[1].axis("off")

        axes[2].imshow(pred, cmap="jet")
        axes[2].set_title(f"Pred (IoU={iou_score:.2f})")
        axes[2].axis("off")

        axes[3].imshow(gt_mask, cmap="gray")
        axes[3].imshow(mismatch, cmap="Reds", alpha=0.6)
        axes[3].set_title("GT + Errors (red)")
        axes[3].axis("off")

        plt.tight_layout()

        # Save each plot with the filename in its title
        os.makedirs(PLOT_PATH, exist_ok=True)
        base = os.path.splitext(os.path.basename(image_paths[idx]))[0]
        out_file = os.path.join(PLOT_PATH, f"inference_{base}_{wrapper.timestamp}.png")
        plt.savefig(out_file)
        print(f"Inference plot saved to: {out_file}")
        plt.close(fig)
