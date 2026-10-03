# training.py
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

import json
import time

import numpy as np
import torch
from torch.utils.data import DataLoader

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


@dataclass
class TrainConfig:
    """Config for a single training run (centralized or client-local)."""
    epochs: int = 30
    lr: float = 1e-3
    weight_decay: float = 0.0
    grad_clip_norm: Optional[float] = 1.0
    device: str = "cpu"
    seed: int = 42

    # outputs
    out_dir: str = "runs"
    run_name: str = "experiment"

    # checkpointing / early stopping
    save_best: bool = True
    monitor: str = "val_rmse"   # key in logged epoch dict
    mode: str = "min"           # "min" or "max"
    patience: int = 10          # 0 disables early stopping

    # logging
    show_progress: bool = True  # tqdm inside epoch
    print_every_epoch: bool = True


@dataclass
class EpochStats:
    epoch: int
    train_loss: float
    train_rmse: float
    train_mae: float
    val_loss: Optional[float] = None
    val_rmse: Optional[float] = None
    val_mae: Optional[float] = None
    test_loss: Optional[float] = None
    test_rmse: Optional[float] = None
    test_mae: Optional[float] = None
    seconds: float = 0.0



def set_seed(seed: int) -> None:
    import random
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)  # safe even if no CUDA


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Returns MSE/RMSE/MAE (JSON-friendly floats)."""
    if y_true.size == 0:
        return {"mse": float("nan"), "rmse": float("nan"), "mae": float("nan")}
    err = y_pred - y_true
    mse = float(np.mean(err ** 2))
    mae = float(np.mean(np.abs(err)))
    return {"mse": mse, "rmse": float(np.sqrt(mse)), "mae": mae}


def _is_better(a: float, b: float, mode: str) -> bool:
    if np.isnan(b):
        return True
    if mode == "min":
        return a < b
    if mode == "max":
        return a > b
    raise ValueError("mode must be 'min' or 'max'")


def save_json(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


def train_one_epoch(
    model: torch.nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    *,
    grad_clip_norm: Optional[float] = 1.0,
    show_pbar: bool = True,
    pbar_desc: str = "train",
) -> Tuple[float, Dict[str, float]]:
    """
    One epoch of regression training (NO AMP/CUDA-SPECIFIC CODE).
    Returns:
      mean_mse_loss, metrics dict (mse/rmse/mae computed from preds)
    """
    model.train()
    loss_fn = torch.nn.MSELoss(reduction="sum")

    loss_sum = 0.0
    n = 0
    y_true_all: List[np.ndarray] = []
    y_pred_all: List[np.ndarray] = []

    it = loader
    if show_pbar and tqdm is not None:
        it = tqdm(loader, desc=pbar_desc, leave=False, dynamic_ncols=True)

    for xb, yb in it:
        xb = xb.to(device)
        yb = yb.to(device).view(-1)

        optimizer.zero_grad(set_to_none=True)

        pred = model(xb).view(-1)
        loss = loss_fn(pred, yb)

        loss.backward()
        if grad_clip_norm is not None:
            torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip_norm)
        optimizer.step()

        loss_sum += float(loss.item())
        n += int(yb.numel())

        y_true_all.append(yb.detach().cpu().numpy())
        y_pred_all.append(pred.detach().cpu().numpy())

        if show_pbar and tqdm is not None:
            # show instantaneous RMSE of the current batch (rough signal)
            batch_rmse = float(torch.sqrt(torch.mean((pred.detach() - yb.detach()) ** 2)).cpu().item())
            it.set_postfix(rmse=f"{batch_rmse:.2f}")

    y_true = np.concatenate(y_true_all, axis=0)
    y_pred = np.concatenate(y_pred_all, axis=0)
    mean_mse = loss_sum / max(n, 1)
    return float(mean_mse), regression_metrics(y_true, y_pred)


@torch.no_grad()
def evaluate(
    model: torch.nn.Module,
    loader: DataLoader,
    device: torch.device,
    *,
    show_pbar: bool = False,
    pbar_desc: str = "eval",
) -> Tuple[float, Dict[str, float]]:
    """Evaluate regression loss and metrics on a loader."""
    model.eval()
    loss_fn = torch.nn.MSELoss(reduction="sum")

    loss_sum = 0.0
    n = 0
    y_true_all: List[np.ndarray] = []
    y_pred_all: List[np.ndarray] = []

    it = loader
    if show_pbar and tqdm is not None:
        it = tqdm(loader, desc=pbar_desc, leave=False, dynamic_ncols=True)

    for xb, yb in it:
        xb = xb.to(device)
        yb = yb.to(device).view(-1)

        pred = model(xb).view(-1)
        loss = loss_fn(pred, yb)

        loss_sum += float(loss.item())
        n += int(yb.numel())

        y_true_all.append(yb.detach().cpu().numpy())
        y_pred_all.append(pred.detach().cpu().numpy())

    y_true = np.concatenate(y_true_all, axis=0) if y_true_all else np.array([], dtype=np.float32)
    y_pred = np.concatenate(y_pred_all, axis=0) if y_pred_all else np.array([], dtype=np.float32)
    mean_mse = loss_sum / max(n, 1)
    return float(mean_mse), regression_metrics(y_true, y_pred)


@torch.no_grad()
def predict(
    model: torch.nn.Module,
    loader: DataLoader,
    device: str = "cpu",
    *,
    show_pbar: bool = False,
) -> Tuple[np.ndarray, np.ndarray]:
    """Return y_true, y_pred arrays (for plotting)."""
    dev = torch.device(device)
    model.eval().to(dev)

    y_true_all: List[np.ndarray] = []
    y_pred_all: List[np.ndarray] = []

    it = loader
    if show_pbar and tqdm is not None:
        it = tqdm(loader, desc="predict", leave=False, dynamic_ncols=True)

    for xb, yb in it:
        xb = xb.to(dev)
        pred = model(xb).view(-1).detach().cpu().numpy()
        y_pred_all.append(pred)
        y_true_all.append(yb.view(-1).detach().cpu().numpy())

    y_true = np.concatenate(y_true_all, axis=0) if y_true_all else np.array([], dtype=np.float32)
    y_pred = np.concatenate(y_pred_all, axis=0) if y_pred_all else np.array([], dtype=np.float32)
    return y_true, y_pred


def train_model(
    model: torch.nn.Module,
    train_loader: DataLoader,
    val_loader: Optional[DataLoader],
    test_loader: Optional[DataLoader],
    cfg: TrainConfig,
    *,
    optimizer_fn: Optional[Callable[[Iterable[torch.nn.Parameter]], torch.optim.Optimizer]] = None,
) -> Dict[str, Any]:
    """
    Modular training wrapper.
    Returns a dict with:
      - model (trained in-memory)
      - history (list of epoch dicts; JSON-friendly)
      - best (epoch/metric info)
      - paths (history + best checkpoint paths)
      - config (as dict)
    """
    set_seed(cfg.seed)
    device = torch.device(cfg.device)
    model = model.to(device)

    if optimizer_fn is None:
        optimizer = torch.optim.Adam(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    else:
        optimizer = optimizer_fn(model.parameters())

    out_dir = Path(cfg.out_dir) / cfg.run_name
    out_dir.mkdir(parents=True, exist_ok=True)

    history: List[Dict[str, Any]] = []
    best_metric = float("nan")
    best_epoch = -1
    bad_epochs = 0
    best_path = out_dir / "best_model.pt"

    for epoch in range(1, cfg.epochs + 1):
        t0 = time.time()

        train_mse, train_m = train_one_epoch(
            model,
            train_loader,
            optimizer,
            device,
            grad_clip_norm=cfg.grad_clip_norm,
            show_pbar=cfg.show_progress,
            pbar_desc=f"Epoch {epoch}/{cfg.epochs}",
        )

        stats = EpochStats(
            epoch=epoch,
            train_loss=float(train_mse),
            train_rmse=float(train_m["rmse"]),
            train_mae=float(train_m["mae"]),
        )

        if val_loader is not None:
            val_mse, val_m = evaluate(model, val_loader, device, show_pbar=False)
            stats.val_loss = float(val_mse)
            stats.val_rmse = float(val_m["rmse"])
            stats.val_mae = float(val_m["mae"])

        if test_loader is not None:
            test_mse, test_m = evaluate(model, test_loader, device, show_pbar=False)
            stats.test_loss = float(test_mse)
            stats.test_rmse = float(test_m["rmse"])
            stats.test_mae = float(test_m["mae"])


        stats.seconds = float(time.time() - t0)
        row = asdict(stats)
        history.append(row)

        # early stopping + checkpoint
        metric_value = row.get(cfg.monitor, None)
        if metric_value is not None and metric_value == metric_value:  # not NaN
            if _is_better(float(metric_value), best_metric, cfg.mode):
                best_metric = float(metric_value)
                best_epoch = epoch
                bad_epochs = 0
                if cfg.save_best:
                    torch.save(
                        {"model_state_dict": model.state_dict(), "epoch": epoch, "metric": best_metric},
                        best_path,
                    )
            else:
                bad_epochs += 1

        # epoch-level ETA
        if cfg.print_every_epoch:
            avg_sec = sum(h["seconds"] for h in history) / len(history)
            eta_sec = avg_sec * (cfg.epochs - epoch)
            val_rmse = row.get("val_rmse", float("nan"))
            test_rmse = row.get("test_rmse", float("nan"))
            print(
                f"Epoch {epoch}/{cfg.epochs} | "
                f"train_rmse={row['train_rmse']:.3f} "
                f"val_rmse={val_rmse:.3f} "
                f"test_rmse={test_rmse:.3f} | "
                f"{row['seconds']:.1f}s/epoch | ETA {eta_sec/60:.1f} min"
            )


        if cfg.patience and bad_epochs >= cfg.patience:
            break

    history_path = out_dir / "history.json"
    save_json(history, history_path)

    return {
        "model": model,
        "history": history,
        "best": {"epoch": best_epoch, "metric": best_metric, "monitor": cfg.monitor, "mode": cfg.mode},
        "paths": {"out_dir": str(out_dir), "history": str(history_path), "best_model": str(best_path)},
        "config": asdict(cfg),
    }
