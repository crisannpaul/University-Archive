# data_cmapss.py
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# Standard CMAPSS format: 26 columns total
# 1 unit, 2 cycle, 3 operational settings, 21 sensors => 26
CMAPSS_COLS = (
    ["unit", "cycle", "os1", "os2", "os3"]
    + [f"s{i}" for i in range(1, 22)]
)

def read_txt(path: str | Path) -> pd.DataFrame:
    """Read CMAPSS train/test txt (whitespace-separated, 26 numeric columns)."""
    path = Path(path)
    df = pd.read_csv(path, sep=r"\s+", header=None, engine="python")
    if df.shape[1] < 26:
        raise ValueError(f"{path.name}: expected >=26 columns, got {df.shape[1]}")
    if df.shape[1] > 26:
        df = df.iloc[:, :26]  # drop trailing empty columns if present
    df.columns = CMAPSS_COLS
    df["unit"] = df["unit"].astype(int)
    df["cycle"] = df["cycle"].astype(int)
    return df

def read_rul(path: str | Path) -> np.ndarray:
    """Read RUL vector (one value per test engine, at last observed cycle)."""
    path = Path(path)
    rul = pd.read_csv(path, sep=r"\s+", header=None, engine="python").iloc[:, 0].to_numpy()
    return rul.astype(np.float32)

def load_split(root_dir: str | Path, dataset_id: str = "FD001") -> Tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    """Load (train_df, test_df, rul_vector) for FD001..FD004."""
    root = Path(root_dir)
    train_path = root / f"train_{dataset_id}.txt"
    test_path = root / f"test_{dataset_id}.txt"
    rul_path = root / f"RUL_{dataset_id}.txt"

    if not train_path.exists():
        raise FileNotFoundError(f"Missing file: {train_path}")
    if not test_path.exists():
        raise FileNotFoundError(f"Missing file: {test_path}")
    if not rul_path.exists():
        raise FileNotFoundError(f"Missing file: {rul_path}")

    train_df = read_txt(train_path)
    test_df = read_txt(test_path)
    rul_vec = read_rul(rul_path)
    return train_df, test_df, rul_vec

def list_units(df: pd.DataFrame) -> List[int]:
    return sorted(df["unit"].unique().tolist())

def rows_per_unit(df: pd.DataFrame) -> pd.Series:
    """Number of rows (cycles) per engine trajectory."""
    return df.groupby("unit").size().sort_index()

def basic_inspection(df: pd.DataFrame) -> Dict[str, float | int]:
    counts = rows_per_unit(df)
    return {
        "num_units": int(counts.shape[0]),
        "total_rows": int(df.shape[0]),
        "min_rows_per_unit": int(counts.min()),
        "max_rows_per_unit": int(counts.max()),
        "mean_rows_per_unit": float(counts.mean()),
        "median_rows_per_unit": float(counts.median()),
    }
