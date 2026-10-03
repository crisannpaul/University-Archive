# fl_client.py
from __future__ import annotations

from typing import Dict, List, Tuple

import flwr as fl
import numpy as np
import torch
from torch.utils.data import DataLoader

from training import train_one_epoch, evaluate


def get_parameters(model: torch.nn.Module) -> List[np.ndarray]:
    """Extract model parameters as a list of NumPy arrays (stable key order)."""
    state_dict = model.state_dict()
    return [v.detach().cpu().numpy() for _, v in state_dict.items()]


def set_parameters(model: torch.nn.Module, parameters: List[np.ndarray]) -> None:
    """Load model parameters from a list of NumPy arrays (same key order as state_dict)."""
    state_dict = model.state_dict()
    keys = list(state_dict.keys())
    if len(parameters) != len(keys):
        raise ValueError(f"Parameter length mismatch: got {len(parameters)} expected {len(keys)}")
    new_state = {k: torch.tensor(p) for k, p in zip(keys, parameters)}
    model.load_state_dict(new_state, strict=True)


class CmapssClient(fl.client.NumPyClient):
    def __init__(
        self,
        model: torch.nn.Module,
        train_loader: DataLoader,
        device: str = "cpu",
        lr: float = 1e-3,
        local_epochs: int = 1,
        grad_clip_norm: float | None = 1.0,
    ):
        self.model = model
        self.train_loader = train_loader
        self.device = torch.device(device)
        self.lr = lr
        self.local_epochs = local_epochs
        self.grad_clip_norm = grad_clip_norm

        self.model.to(self.device)

    def get_parameters(self, config):
        return get_parameters(self.model)

    def fit(self, parameters, config):
        set_parameters(self.model, parameters)

        # Allow server to override local settings per round
        local_epochs = int(config.get("local_epochs", self.local_epochs))
        lr = float(config.get("lr", self.lr))

        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)

        # Local training
        last_metrics = {}
        for _ in range(local_epochs):
            _, m = train_one_epoch(
                self.model,
                self.train_loader,
                optimizer,
                self.device,
                grad_clip_norm=self.grad_clip_norm,
                show_pbar=False,
            )
            last_metrics = m

        num_examples = len(self.train_loader.dataset)
        return get_parameters(self.model), num_examples, {
            "train_rmse": float(last_metrics.get("rmse", float("nan"))),
            "train_mae": float(last_metrics.get("mae", float("nan"))),
        }

    def evaluate(self, parameters, config):
        # Optional: client-side evaluation (not needed for FedAvg)
        set_parameters(self.model, parameters)
        loss, m = evaluate(self.model, self.train_loader, self.device, show_pbar=False)
        num_examples = len(self.train_loader.dataset)
        return float(loss), num_examples, {
            "train_rmse": float(m.get("rmse", float("nan"))),
            "train_mae": float(m.get("mae", float("nan"))),
        }
