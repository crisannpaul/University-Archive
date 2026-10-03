import time
import os
import matplotlib.pyplot as plt
import numpy as np
import torch

from torch.nn import CrossEntropyLoss
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader
from segmentation_models_pytorch.losses import DiceLoss

from config import *
from dataset import CholecSegDataset
from model import ModelWrapper, compute_iou


def train(
    model_wrapper,
    num_epochs: int = 10,
    batch_size: int = BATCH_SIZE,
    lr: float = 1e-4,
    patience: int = 5
):
    os.makedirs(MODEL_PATH, exist_ok=True)
    os.makedirs(PLOT_PATH,  exist_ok=True)

    device    = DEVICE
    timestamp = model_wrapper.timestamp

    # 1) collect train and test file lists from pre‐split folders
    train_imgs = sorted([
        os.path.join(TRAIN_IMAGES_DIR, f)
        for f in os.listdir(TRAIN_IMAGES_DIR) if f.lower().endswith(".png")
    ])
    train_masks = sorted([
        os.path.join(TRAIN_MASKS_DIR, f)
        for f in os.listdir(TRAIN_MASKS_DIR) if f.lower().endswith(".png")
    ])
    val_imgs = sorted([
        os.path.join(TEST_IMAGES_DIR, f)
        for f in os.listdir(TEST_IMAGES_DIR) if f.lower().endswith(".png")
    ])
    val_masks = sorted([
        os.path.join(TEST_MASKS_DIR, f)
        for f in os.listdir(TEST_MASKS_DIR) if f.lower().endswith(".png")
    ])

    # 2) create DataLoaders (no train_test_split needed)
    train_ds = CholecSegDataset(train_imgs, train_masks)
    val_ds   = CholecSegDataset(val_imgs,   val_masks)
    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        num_workers=os.cpu_count(),
        pin_memory=True
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=os.cpu_count(),
        pin_memory=True
    )

    # 3) model, optimizer, scheduler, losses
    model     = model_wrapper.model.to(device)
    optimizer = AdamW(model.parameters(), lr=lr)
    scheduler = CosineAnnealingLR(optimizer, T_max=num_epochs)
    ce_loss   = CrossEntropyLoss()
    dice_loss = DiceLoss(mode="multiclass")

    history = {"train_loss": [], "val_loss": [], "mIoU": []}

    best_val_loss     = float("inf")
    epochs_no_improve = 0

    total_start = time.time()

    for epoch in range(1, num_epochs + 1):
        epoch_start = time.time()

        # — training —
        model.train()
        running_train = 0.0
        for imgs_batch, masks_batch in train_loader:
            imgs_batch = imgs_batch.to(device)
            masks_batch = masks_batch.to(device)

            logits    = model_wrapper.predict(imgs_batch)
            loss_ce   = ce_loss(logits, masks_batch)
            loss_dice = dice_loss(logits, masks_batch)
            loss      = loss_ce + loss_dice

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_train += loss.item()

        avg_train = running_train / len(train_loader)

        # — validation —
        model.eval()
        running_val = 0.0
        val_ious    = []

        with torch.no_grad():
            for imgs_batch, masks_batch in val_loader:
                imgs_batch = imgs_batch.to(device)
                masks_batch = masks_batch.to(device)

                logits    = model_wrapper.predict(imgs_batch)
                loss_ce   = ce_loss(logits, masks_batch)
                loss_dice = dice_loss(logits, masks_batch)
                loss      = loss_ce + loss_dice

                running_val += loss.item()
                preds = logits.argmax(dim=1)
                val_ious.append(
                    np.nanmean(compute_iou(preds, masks_batch, NUM_CLASSES))
                )

        avg_val = running_val / len(val_loader)
        avg_iou = np.nanmean(val_ious)

        history["train_loss"].append(avg_train)
        history["val_loss"].append(avg_val)
        history["mIoU"].append(avg_iou)

        epoch_time = time.time() - epoch_start
        print(
            f"[Epoch {epoch}/{num_epochs}]  "
            f"train_loss={avg_train:.4f}  val_loss={avg_val:.4f}  mIoU={avg_iou:.4f}  "
            f"(epoch time: {epoch_time:.1f}s)"
        )

        # — checkpoint & early stopping —
        if avg_val < best_val_loss:
            best_val_loss     = avg_val
            epochs_no_improve = 0
            best_path = os.path.join(MODEL_PATH, f"best_{timestamp}.pth")
            torch.save(model.state_dict(), best_path)
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                print(f"No improvement for {patience} epochs → stopping early.")
                break

        if epoch % 10 == 0:
            chkpt = os.path.join(MODEL_PATH, f"model_{timestamp}_{epoch}.pth")
            torch.save(model.state_dict(), chkpt)

        scheduler.step()

    total_time = time.time() - total_start
    print(f"Total training time: {total_time:.1f}s ({total_time/len(history['train_loss']):.1f}s/epoch)")

    # — plot training curves —
    epochs = range(1, len(history["train_loss"]) + 1)
    plt.figure(figsize=(8,4))
    plt.plot(epochs, history["train_loss"], label="Train Loss")
    plt.plot(epochs, history["val_loss"],   label="Val Loss")
    plt.plot(epochs, history["mIoU"],       label="mIoU")
    plt.xlabel("Epoch")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plot_file = os.path.join(PLOT_PATH, f"training_results_{timestamp}.png")
    plt.savefig(plot_file)
    print(f"[Done] metrics plot saved to {plot_file}")
