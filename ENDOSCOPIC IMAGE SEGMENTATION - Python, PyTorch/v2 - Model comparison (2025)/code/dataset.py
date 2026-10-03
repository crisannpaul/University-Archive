# dataset.py
import os
import numpy as np
from PIL import Image
import torch
from PIL.Image import Resampling
from torch.utils.data import Dataset
from torchvision import transforms
from config import *

class CholecSegDataset(Dataset):
    """
    Dataset for CholecSeg8K: loads images & masks, resizes to a fixed size,
    applies ImageNet normalization, and remaps mask values to [0..num_classes-1].
    """
    def __init__(self, image_paths, mask_paths, mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)):
        self.image_paths = image_paths
        self.mask_paths  = mask_paths
        self.mean        = mean
        self.std         = std
        self.image_size  = (IMAGE_HEIGHT, IMAGE_WIDTH)

        self.img_transform = transforms.Compose([
            transforms.Resize(self.image_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ])

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        # 1) load & normalize image
        img = Image.open(self.image_paths[idx]).convert("RGB")
        img = self.img_transform(img)

        # 2) load & remap mask
        mask = Image.open(self.mask_paths[idx]).convert("L")
        mask = mask.resize(self.image_size, resample=Resampling.NEAREST)
        mask = np.array(mask)
        mask = (mask / 255.0 * (NUM_CLASSES - 1)).round().astype(np.uint8)
        mask = torch.from_numpy(mask).long()

        return img, mask