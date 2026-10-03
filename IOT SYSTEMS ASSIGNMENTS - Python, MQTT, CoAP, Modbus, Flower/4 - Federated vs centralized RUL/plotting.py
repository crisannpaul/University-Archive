
# plotting.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
import json

import numpy as np
import matplotlib.pyplot as plt


def load_history(path: str | Path) -> List[Dict[str, Any]]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _extract(history: List[Dict[str, Any]], key: str) -> Tuple[np.ndarray, np.ndarray]:
    x = np.array([row["epoch"] for row in history], dtype=np.int32)
    y = np.array([row.get(key, np.nan) for row in history], dtype=np.float32)
    return x, y


def plot_histories(
    histories: Sequence[List[Dict[str, Any]]],
    labels: Sequence[str],
    key: str,
    *,
    title: Optional[str] = None,
    save_path: Optional[str | Path] = None,
    show: bool = True,
):
    """
    Unified plot for one metric across multiple runs.
    keys: train_rmse, val_rmse, train_loss, val_loss, etc.
    """
    if len(histories) != len(labels):
        raise ValueError("histories and labels must have the same length.")

    plt.figure()
    for hist, lab in zip(histories, labels):
        x, y = _extract(hist, key)
        plt.plot(x, y, label=lab)

    plt.xlabel("Epoch")
    plt.ylabel(key)
    plt.title(title or key)
    plt.grid(True, alpha=0.3)
    plt.legend()

    if save_path is not None:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, bbox_inches="tight", dpi=160)

    if show:
        plt.show()
    else:
        plt.close()

def plot_train_val_test(
    history: List[Dict[str, Any]],
    *,
    metric: str = "rmse",  # or "loss", "mae"
    title: Optional[str] = None,
    save_path: Optional[str | Path] = None,
    show: bool = True,
):
    """
    One plot with train/val/test for a single run.
    Expects keys like: train_rmse, val_rmse, test_rmse (or *_loss, *_mae).
    """
    plt.figure()

    for split in ["train", "val", "test"]:
        key = f"{split}_{metric}"
        x, y = _extract(history, key)
        # only plot if it exists (not all histories will have test)
        if not np.all(np.isnan(y)):
            plt.plot(x, y, label=split)

    plt.xlabel("Epoch")
    plt.ylabel(metric)
    plt.title(title or f"{metric}: train vs val vs test")
    plt.grid(True, alpha=0.3)
    plt.legend()

    if save_path is not None:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, bbox_inches="tight", dpi=160)

    if show:
        plt.show()
    else:
        plt.close()


def summary_regression(y_true: np.ndarray, y_pred: np.ndarray, *, tol_cycles: float = 10.0) -> Dict[str, float]:
    """
    Expressive numeric summary:
      - rmse, mae
      - median absolute error
      - 90th percentile absolute error
      - percent within tolerance (default 10 cycles)
    """
    y_true = np.asarray(y_true).reshape(-1)
    y_pred = np.asarray(y_pred).reshape(-1)
    err = y_pred - y_true
    abs_err = np.abs(err)

    mse = float(np.mean(err ** 2)) if err.size else float("nan")
    rmse = float(np.sqrt(mse)) if err.size else float("nan")
    mae = float(np.mean(abs_err)) if abs_err.size else float("nan")
    med_ae = float(np.median(abs_err)) if abs_err.size else float("nan")
    p90_ae = float(np.percentile(abs_err, 90)) if abs_err.size else float("nan")
    within = float(np.mean(abs_err <= tol_cycles)) if abs_err.size else float("nan")

    return {
        "rmse": rmse,
        "mae": mae,
        "median_abs_error": med_ae,
        "p90_abs_error": p90_ae,
        f"pct_within_{int(tol_cycles)}_cycles": within,
    }


def plot_pred_vs_true(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    title: str = "Predicted vs True RUL",
    save_path: Optional[str | Path] = None,
    show: bool = True,
):
    """
    Scatter plot for a quick sanity check.
    Ideal: points on the diagonal.
    """
    y_true = np.asarray(y_true).reshape(-1)
    y_pred = np.asarray(y_pred).reshape(-1)

    plt.figure()
    plt.scatter(y_true, y_pred, s=10, alpha=0.5)

    mn = float(min(y_true.min(), y_pred.min()))
    mx = float(max(y_true.max(), y_pred.max()))
    plt.plot([mn, mx], [mn, mx])

    plt.xlabel("True RUL")
    plt.ylabel("Predicted RUL")
    plt.title(title)
    plt.grid(True, alpha=0.3)

    if save_path is not None:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, bbox_inches="tight", dpi=160)

    if show:
        plt.show()
    else:
        plt.close()


def plot_error_hist(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    bins: int = 50,
    title: str = "Error histogram (pred - true)",
    save_path: Optional[str | Path] = None,
    show: bool = True,
):
    y_true = np.asarray(y_true).reshape(-1)
    y_pred = np.asarray(y_pred).reshape(-1)
    err = y_pred - y_true

    plt.figure()
    plt.hist(err, bins=bins, alpha=0.85)
    plt.xlabel("Error (cycles)")
    plt.ylabel("Count")
    plt.title(title)
    plt.grid(True, alpha=0.3)

    if save_path is not None:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, bbox_inches="tight", dpi=160)

    if show:
        plt.show()
    else:
        plt.close()


def plot_compare_all_splits(
    centralized_history: List[Dict[str, Any]],
    federated_history: List[Dict[str, Any]],
    *,
    metric: str = "rmse",
    title: str = "Centralized vs Federated (train/val/test)",
    save_path: Optional[str | Path] = None,
    show: bool = True,
):
    """
    One plot with 6 lines:
      centralized train/val/test (Blues)
      federated   train/val/test (Reds)

    Uses keys like train_rmse, val_rmse, test_rmse.
    """
    plt.figure()

    blues = plt.cm.Blues
    reds = plt.cm.Reds

    # shades: lighter -> darker
    c_colors = [blues(0.45), blues(0.65), blues(0.85)]
    f_colors = [reds(0.45), reds(0.65), reds(0.85)]
    splits = ["train", "val", "test"]

    for split, color in zip(splits, c_colors):
        key = f"{split}_{metric}"
        x, y = _extract(centralized_history, key)
        if not np.all(np.isnan(y)):
            plt.plot(x, y, label=f"centralized {split}", color=color)

    for split, color in zip(splits, f_colors):
        key = f"{split}_{metric}"
        x, y = _extract(federated_history, key)
        if not np.all(np.isnan(y)):
            plt.plot(x, y, label=f"federated {split}", color=color)

    plt.xlabel("Epoch / Round")
    plt.ylabel(metric)
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.legend()

    if save_path is not None:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, bbox_inches="tight", dpi=160)

    if show:
        plt.show()
    else:
        plt.close()
