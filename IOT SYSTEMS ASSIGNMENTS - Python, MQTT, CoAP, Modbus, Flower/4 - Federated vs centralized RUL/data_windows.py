# data_windows.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader

from data_cmapss import load_split


# -------------------------
# RUL labeling (with cap)
# -------------------------

def add_rul_train(train_df: pd.DataFrame, *, early_rul: Optional[float] = 125.0) -> pd.DataFrame:
    """
    Train is run-to-failure:
      RUL = max_cycle(unit) - cycle
    Optional: cap RUL at early_rul (piecewise linear degradation target).
    """
    df = train_df.copy()
    max_cycle = df.groupby("unit")["cycle"].max()
    df["rul"] = (max_cycle[df["unit"]].to_numpy() - df["cycle"].to_numpy()).astype(np.float32)

    if early_rul is not None:
        df["rul"] = df["rul"].clip(upper=float(early_rul))

    return df


def add_rul_test(test_df: pd.DataFrame, rul_vec: np.ndarray, *, early_rul: Optional[float] = 125.0) -> pd.DataFrame:
    """
    rul_vec gives RUL at last observed cycle for each test unit.
    Label each row:
      RUL(t) = RUL_last(unit) + (last_cycle(unit) - cycle(t))
    Optional: cap at early_rul.
    """
    df = test_df.copy()
    last_cycle = df.groupby("unit")["cycle"].max().sort_index()
    units = last_cycle.index.to_numpy()

    if len(rul_vec) != len(units):
        raise ValueError(f"RUL length ({len(rul_vec)}) != #test units ({len(units)})")

    rul_last_by_unit = pd.Series(rul_vec.astype(np.float32), index=units)
    df["rul"] = (
        rul_last_by_unit[df["unit"]].to_numpy()
        + (last_cycle[df["unit"]].to_numpy() - df["cycle"].to_numpy()).astype(np.float32)
    ).astype(np.float32)

    if early_rul is not None:
        df["rul"] = df["rul"].clip(upper=float(early_rul))

    return df


def default_feature_cols(df: pd.DataFrame) -> List[str]:
    drop = {"unit", "cycle", "rul"}
    return [c for c in df.columns if c not in drop]


# -------------------------
# Feature preprocessing
# -------------------------

def compute_feature_preproc(
    train_df: pd.DataFrame,
    feature_cols: List[str],
    *,
    const_std_eps: float = 1e-8,
) -> Dict[str, object]:
    """
    Fit preprocessing on TRAIN ONLY:
      - drop constant/near-constant cols
      - z-score stats (mean/std) for remaining cols
    """
    std = train_df[feature_cols].std()
    keep_cols = std[std > const_std_eps].index.tolist()

    mu = train_df[keep_cols].mean()
    sigma = train_df[keep_cols].std().replace(0, 1.0)

    return {
        "feature_cols": keep_cols,
        "mu": mu,
        "sigma": sigma,
        "dropped_constant_cols": [c for c in feature_cols if c not in keep_cols],
    }


def apply_feature_preproc(df: pd.DataFrame, preproc: Dict[str, object]) -> pd.DataFrame:
    """Apply fitted preprocessing (z-score) and keep only selected feature cols + id cols + rul."""
    out = df.copy()
    cols = preproc["feature_cols"]  # type: ignore[assignment]
    mu = preproc["mu"]              # type: ignore[assignment]
    sigma = preproc["sigma"]        # type: ignore[assignment]

    # keep id/target, but standardize only feature cols
    out[cols] = (out[cols] - mu) / sigma
    return out


# -------------------------
# Window datasets
# -------------------------

@dataclass(frozen=True)
class WindowConfig:
    seq_len: int = 30
    stride: int = 1
    feature_cols: Optional[List[str]] = None
    target_col: str = "rul"


class WindowDataset(Dataset):
    """Sliding windows over each unit. y is target at end of window."""
    def __init__(self, df: pd.DataFrame, cfg: WindowConfig):
        super().__init__()
        self.df = df.sort_values(["unit", "cycle"]).reset_index(drop=True)
        self.cfg = cfg

        if cfg.feature_cols is None:
            raise ValueError("WindowDataset requires cfg.feature_cols (fixed after preprocessing).")
        self.feature_cols = cfg.feature_cols

        self.X = self.df[self.feature_cols].to_numpy(dtype=np.float32)
        self.y = self.df[self.cfg.target_col].to_numpy(dtype=np.float32)


        self._windows: List[Tuple[int, int]] = []
        for _, g in self.df.groupby("unit", sort=True):
            idx = g.index.to_numpy()
            n = len(idx)
            for end_pos in range(cfg.seq_len - 1, n, cfg.stride):
                start_pos = end_pos - (cfg.seq_len - 1)
                self._windows.append((int(idx[start_pos]), int(idx[end_pos])))

        if len(self._windows) == 0:
            raise ValueError("No windows created. Lower seq_len or check data.")

    def __len__(self) -> int:
        return len(self._windows)

    def __getitem__(self, i: int):
        start, end = self._windows[i]
        x = self.X[start:end+1]              # end inclusive
        y = np.float32(self.y[end])
        return torch.from_numpy(x), torch.tensor(y, dtype=torch.float32)



class LastWindowPerUnitDataset(Dataset):
    """One sample per unit: last seq_len cycles, target = RUL at last observed cycle."""
    def __init__(self, df: pd.DataFrame, cfg: WindowConfig):
        super().__init__()
        self.df = df.sort_values(["unit", "cycle"]).reset_index(drop=True)
        self.cfg = cfg

        if cfg.feature_cols is None:
            raise ValueError("LastWindowPerUnitDataset requires cfg.feature_cols.")
        self.feature_cols = cfg.feature_cols

        self._slices: List[Tuple[int, int]] = []
        for u, g in self.df.groupby("unit", sort=True):
            if len(g) < cfg.seq_len:
                continue
            end = int(g.index.max())
            start = int(end - (cfg.seq_len - 1))
            self._slices.append((start, end))

        if len(self._slices) == 0:
            raise ValueError("No last-windows created. Lower seq_len or check data.")

    def __len__(self) -> int:
        return len(self._slices)

    def __getitem__(self, i: int):
        start, end = self._slices[i]
        x = self.df.loc[start:end, self.feature_cols].to_numpy(dtype=np.float32)
        y = np.float32(self.df.loc[end, self.cfg.target_col])
        return torch.from_numpy(x), torch.tensor(y, dtype=torch.float32)


# -------------------------
# Splitting + loader builders
# -------------------------

def split_train_val_by_unit(train_df: pd.DataFrame, val_ratio: float = 0.1, seed: int = 42):
    if not (0.0 < val_ratio < 1.0):
        raise ValueError("val_ratio must be in (0,1)")
    units = sorted(train_df["unit"].unique().tolist())
    rng = np.random.default_rng(seed)
    rng.shuffle(units)
    n_val = max(1, int(round(len(units) * val_ratio)))
    val_units = set(units[:n_val])
    tr = train_df[~train_df["unit"].isin(val_units)].copy()
    va = train_df[train_df["unit"].isin(val_units)].copy()
    return tr, va


def make_centralized_loaders(
    root_dir: str | Path,
    dataset_id: str = "FD001",
    *,
    seq_len: int = 30,
    stride: int = 1,
    batch_size: int = 64,
    num_workers: int = 0,
    val_ratio: float = 0.1,
    seed: int = 42,
    early_rul: Optional[float] = 125.0,
    eval_last_window_only: bool = True,
) -> Dict[str, object]:
    """
    Centralized loaders with standard CMAPSS preprocessing:
      - piecewise RUL cap (early_rul)
      - drop constant sensors (fit on train)
      - z-score normalize (fit on train)
    """
    train_df, test_df, rul_vec = load_split(root_dir, dataset_id)

    train_df = add_rul_train(train_df, early_rul=early_rul)
    test_df = add_rul_test(test_df, rul_vec, early_rul=early_rul)

    tr_df, va_df = split_train_val_by_unit(train_df, val_ratio=val_ratio, seed=seed)

    feat_cols = default_feature_cols(tr_df)
    preproc = compute_feature_preproc(tr_df, feat_cols)

    tr_df = apply_feature_preproc(tr_df, preproc)
    va_df = apply_feature_preproc(va_df, preproc)
    test_df = apply_feature_preproc(test_df, preproc)

    used_feature_cols: List[str] = preproc["feature_cols"]  # type: ignore[assignment]

    cfg = WindowConfig(seq_len=seq_len, stride=stride, feature_cols=used_feature_cols)

    train_ds = WindowDataset(tr_df, cfg)
    val_ds = WindowDataset(va_df, cfg)

    if eval_last_window_only:
        test_ds = LastWindowPerUnitDataset(test_df, cfg)
    else:
        test_ds = WindowDataset(test_df, cfg)

    loaders: Dict[str, object] = {
        "train": DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers),
        "val": DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers),
        "test": DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers),
        "meta": {
            "num_features": len(used_feature_cols),
            "feature_cols": used_feature_cols,
            "dropped_constant_cols": preproc["dropped_constant_cols"],
            "early_rul": early_rul,
        },
    }
    return loaders


# -------------------------
# Federated partitioning
# -------------------------

from typing import Any


def partition_units(
    units: List[int],
    num_clients: int = 10,
    seed: int = 42,
) -> List[List[int]]:
    """
    Shuffle units and split into num_clients groups as evenly as possible.
    Example: 100 units -> 10 groups of ~10.
    """
    rng = np.random.default_rng(seed)
    units = units.copy()
    rng.shuffle(units)
    return [units[i::num_clients] for i in range(num_clients)]


def make_federated_loaders(
    root_dir: str | Path,
    dataset_id: str = "FD001",
    *,
    num_clients: int = 10,
    seq_len: int = 50,
    stride: int = 1,
    batch_size: int = 128,
    num_workers: int = 0,
    val_ratio: float = 0.1,
    seed: int = 42,
    early_rul: Optional[float] = 125.0,
    eval_last_window_only: bool = True,
) -> Dict[str, Any]:
    """
    Creates:
      - client_loaders: list of DataLoaders, one per client (each client has multiple engines)
      - val_loader: global validation loader (held-out engines)
      - test_loader: global test loader
      - meta: feature info + client unit groups

    IMPORTANT: Preprocessing (feature drop + z-score) is fit on TRAIN ONLY,
    then applied to train/val/test and shared across clients (fair + stable baseline).
    """
    train_df, test_df, rul_vec = load_split(root_dir, dataset_id)

    train_df = add_rul_train(train_df, early_rul=early_rul)
    test_df = add_rul_test(test_df, rul_vec, early_rul=early_rul)

    # global train/val split by unit (avoid leakage)
    tr_df, va_df = split_train_val_by_unit(train_df, val_ratio=val_ratio, seed=seed)

    # fit preprocessing on global train (same as centralized)
    feat_cols = default_feature_cols(tr_df)
    preproc = compute_feature_preproc(tr_df, feat_cols, const_std_eps=1e-3)

    tr_df = apply_feature_preproc(tr_df, preproc)
    va_df = apply_feature_preproc(va_df, preproc)
    test_df = apply_feature_preproc(test_df, preproc)

    used_feature_cols: List[str] = preproc["feature_cols"]  # type: ignore[assignment]
    wcfg = WindowConfig(seq_len=seq_len, stride=stride, feature_cols=used_feature_cols)

    # build client partitions from TRAIN units only
    train_units = sorted(tr_df["unit"].unique().tolist())
    client_unit_groups = partition_units(train_units, num_clients=num_clients, seed=seed)

    client_loaders: List[DataLoader] = []
    for units in client_unit_groups:
        client_df = tr_df[tr_df["unit"].isin(units)].copy()
        client_ds = WindowDataset(client_df, wcfg)
        client_loaders.append(
            DataLoader(client_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers)
        )

    # global val/test loaders
    val_ds = WindowDataset(va_df, wcfg)

    if eval_last_window_only:
        test_ds = LastWindowPerUnitDataset(test_df, wcfg)
    else:
        test_ds = WindowDataset(test_df, wcfg)

    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    return {
        "client_loaders": client_loaders,
        "val_loader": val_loader,
        "test_loader": test_loader,
        "meta": {
            "num_clients": num_clients,
            "client_unit_groups": client_unit_groups,
            "num_features": len(used_feature_cols),
            "feature_cols": used_feature_cols,
            "dropped_constant_cols": preproc["dropped_constant_cols"],
            "early_rul": early_rul,
            "dataset_id": dataset_id,
            "seq_len": seq_len,
            "batch_size": batch_size,
        },
    }
