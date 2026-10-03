import os
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
from transformers import SegformerForSemanticSegmentation
import numpy as np

# 1. Dataset definition with 13 classes and original image size
class SegmentationDataset(Dataset):
    def __init__(self, image_dir, mask_dir, img_size=(512, 512)):
        self.image_dir = image_dir
        self.mask_dir = mask_dir
        self.images = sorted(os.listdir(image_dir))
        self.masks = sorted(os.listdir(mask_dir))
        self.transform_img = transforms.Compose([
            transforms.Resize(img_size, interpolation=Image.BILINEAR),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        self.img_size = img_size
        # Mapping grayscale values to class indices
        self.gray2class = {
            50: 0,  # Background
            11: 1,  # Abdominal Wall
            21: 2,  # Liver
            13: 3,  # GI Tract
            12: 4,  # Fat
            31: 5,  # Grasper
            23: 6,  # Connective Tissue
            24: 7,  # Blood
            25: 8,  # Cystic Duct
            32: 9,  # L-hook
            22: 10, # Gallbladder
            33: 11, # Hepatic Vein
            5: 12   # Liver Ligament
        }

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = os.path.join(self.image_dir, self.images[idx])
        mask_path = os.path.join(self.mask_dir, self.masks[idx])

        image = Image.open(img_path).convert("RGB")
        mask = Image.open(mask_path).convert("L")  # grayscale mask

        # transform image
        image = self.transform_img(image)
        # resize mask and convert to numpy
        mask = mask.resize(self.img_size, Image.NEAREST)
        mask_np = np.array(mask, dtype=np.uint8)

        # map grayscale to class indices
        mask_cls = np.zeros_like(mask_np, dtype=np.int64)
        for gray_val, cls_idx in self.gray2class.items():
            mask_cls[mask_np == gray_val] = cls_idx
        mask = torch.from_numpy(mask_cls)

        return image, mask

def main():
    # 2. Paths and parameters
    train_img_dir = "dataset/train/images"
    train_mask_dir = "dataset/train/masks"
    val_split = 0.1
    batch_size = 4
    lr = 5e-5
    num_epochs = 10
    num_classes = 13

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 3. Prepare datasets and loaders
    full_dataset = SegmentationDataset(train_img_dir, train_mask_dir)
    val_size = int(len(full_dataset) * val_split)
    train_size = len(full_dataset) - val_size
    train_dataset, val_dataset = torch.utils.data.random_split(full_dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=1, shuffle=False, num_workers=1)

    # 4. Model and optimizer
    model = SegformerForSemanticSegmentation.from_pretrained(
        "nvidia/segformer-b0-finetuned-ade-512-512",
        num_labels=num_classes,
        ignore_mismatched_sizes=True
    ).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)

    # 5. Training loop
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0.0
        for images, masks in train_loader:
            images = images.to(device)
            masks = masks.to(device)

            outputs = model(pixel_values=images, labels=masks)
            loss = outputs.loss
            total_loss += loss.item()

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        avg_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch+1}/{num_epochs} - Training Loss: {avg_loss:.4f}")

    # 6. Evaluation - compute mean IoU over 13 classes
    def compute_iou(preds, labels, num_classes=13):
        ious = []
        for cls in range(num_classes):
            pred_inds = (preds == cls)
            target_inds = (labels == cls)
            intersection = (pred_inds & target_inds).sum().item()
            union = (pred_inds | target_inds).sum().item()
            if union == 0:
                ious.append(float('nan'))
            else:
                ious.append(intersection / union)
        return ious

    model.eval()
    all_ious = []
    with torch.no_grad():
        for images, masks in val_loader:
            images = images.to(device)
            masks = masks.to(device)

            outputs = model(pixel_values=images)
            logits = outputs.logits  # [1, num_labels, H, W]
            preds = torch.argmax(logits, dim=1)

            ious = compute_iou(preds.cpu(), masks.cpu(), num_classes)
            all_ious.append(ious)

    # average per-class and overall IoU
    ious_arr = np.array(all_ious)
    mean_ious = np.nanmean(ious_arr, axis=0)
    mean_iou = np.nanmean(mean_ious)
    print(f"Mean IoU per class: {mean_ious}")
    print(f"Overall Mean IoU: {mean_iou:.4f}")

    # 7. Save the trained model
    os.makedirs("outputs", exist_ok=True)
    model_path = os.path.join("outputs", "segformer_b0_cholecseg.pth")
    torch.save(model.state_dict(), model_path)
    print(f"Model saved to {model_path}")


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()
    main()