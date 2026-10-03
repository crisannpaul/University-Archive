# custom_model_with_resnet.py
import datetime

import torch
import glob
import os
import numpy as np
from torchvision.models.segmentation import deeplabv3_resnet50
from config import *

def compute_iou(preds: torch.Tensor, labels: torch.Tensor, num_classes: int = NUM_CLASSES) -> np.ndarray:
    """
    Compute per-class IoU. Returns array of shape (num_classes,).
    """
    preds  = preds.view(-1)
    labels = labels.view(-1)
    ious = []
    for cls in range(num_classes):
        pred_inds  = preds  == cls
        label_inds = labels == cls
        inter = (pred_inds & label_inds).sum().item()
        union = int(pred_inds.sum().item() + label_inds.sum().item() - inter)
        ious.append(float('nan') if union == 0 else inter / union)
    return np.array(ious)

def denormalize(img_tensor: torch.Tensor, mean: tuple, std: tuple) -> np.ndarray:
    """
    Inverse of torchvision normalization.
    - img_tensor: FloatTensor of shape (3, H, W), normalized with given mean/std.
    - mean, std: 3‐tuples used in the original normalization.
    Returns an H×W×3 NumPy array in [0..1].
    """
    # clone to avoid modifying the original tensor
    img = img_tensor.clone().cpu()
    for c in range(3):
        img[c] = img[c] * std[c] + mean[c]
    # CHW -> HWC
    img = img.permute(1, 2, 0).numpy()
    # clamp to valid range
    return np.clip(img, 0.0, 1.0)

class ModelWrapper:
    """
    Wraps DeepLab v3+ with methods for training, saving & loading.
    """
    def __init__(self, name, model):
        self.name = name

        self.model = model
        self.model.to(DEVICE)

        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    def predict(self, x: torch.Tensor) -> torch.Tensor:
        """
        Run a forward pass and return the raw logits tensor (B, C, H, W)
        no matter whether the wrapped model returns a dict or a bare tensor.
        """
        y = self.model(x)
        # segmentation_models_pytorch (SegFormer, PSPNet, etc) returns a Tensor
        # torchvision's deeplabv3 returns a dict { 'out': Tensor, ... }
        return y["out"] if isinstance(y, dict) else y

    def load_latest(self):
        """
        Finds the newest checkpoint in `folder` matching `pattern` and loads it.
        """
        files = glob.glob(os.path.join(MODEL_PATH, "*.pth"))
        if not files:
            raise FileNotFoundError(f"No checkpoints found in {MODEL_PATH}")
        latest = max(files, key=os.path.getctime)
        state = torch.load(latest, map_location=DEVICE)
        self.model.load_state_dict(state)
        return latest
