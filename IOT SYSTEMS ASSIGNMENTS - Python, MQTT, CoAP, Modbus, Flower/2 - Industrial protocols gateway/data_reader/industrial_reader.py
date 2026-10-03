import pandas as pd
import numpy as np
import random
from pathlib import Path
import matplotlib.pyplot as plt


class IndustrialDatasetReader:
    """
    Reader + preprocessor for the industrial equipment dataset (chicago.csv).

    Behavior:
      - Loads dataset
      - Keeps only: pressure, vibration, humidity
      - For rows where faulty == 1, replaces those sensor values with NaN
      - Handles missing values via forward-fill + backward-fill
      - Provides fixed-length shards for simulated devices:
            random start index inside valid range
            length = shard_len (parameter)
    """

    def __init__(self, path: str):
        self.path = Path(path)
        self.df = None
        self.length = None

        self._load()
        self._preprocess()

    # ----------------------------------------------------------------------
    # Loading + preprocessing
    # ----------------------------------------------------------------------
    def _load(self):
        """Loads CSV into a DataFrame."""
        if not self.path.exists():
            raise FileNotFoundError(f"Dataset not found at: {self.path}")

        # We only need these columns, plus faulty flag for cleaning
        self.df = pd.read_csv(
            self.path,
            usecols=["pressure", "vibration", "humidity", "faulty"],
        )
        print(f"[IndustrialDatasetReader] Loaded dataset with {len(self.df)} rows.")

    def _preprocess(self):
        """
        Cleans sensor values:
          - For rows with faulty == 1, set sensor columns to NaN
          - Forward/backward fill missing values
        Keeps only sensor columns in the final frame.
        """
        sensor_cols = ["pressure", "vibration", "humidity"]

        # Ensure columns exist
        expected_cols = sensor_cols + ["faulty"]
        missing = [c for c in expected_cols if c not in self.df.columns]
        if missing:
            raise ValueError(f"Missing expected columns in Industrial dataset: {missing}")

        # Convert faulty to numeric (defensive in case it's string)
        self.df["faulty"] = pd.to_numeric(self.df["faulty"], errors="coerce").fillna(0)

        # Replace sensor cells with NaN where faulty == 1
        faulty_mask = self.df["faulty"] == 1
        self.df.loc[faulty_mask, sensor_cols] = np.nan

        # Forward + backward fill each sensor column
        for col in sensor_cols:
            self.df[col] = self.df[col].ffill().bfill()

        # Drop any rows that still have NaN in sensor columns
        self.df.dropna(subset=sensor_cols, inplace=True)

        # Keep only sensor columns from here on
        self.df = self.df[sensor_cols].reset_index(drop=True)
        self.length = len(self.df)

        print(f"[IndustrialDatasetReader] Preprocessed dataset, final rows: {self.length}")

    # ----------------------------------------------------------------------
    # Shard selection
    # ----------------------------------------------------------------------
    def get_shard(self, shard_len: int):
        """
        Returns a fixed-length shard (DataFrame) of size `shard_len`.

        - Picks a random start index such that the shard fits entirely
          inside [0, length).
        - Returns a copy of the slice with reset index.
        """
        if shard_len <= 0:
            raise ValueError("shard_len must be positive.")

        if self.length is None or self.length == 0:
            raise ValueError("Dataset is empty; cannot create shard.")

        if shard_len > self.length:
            raise ValueError(
                f"Requested shard_len={shard_len} larger than dataset length={self.length}."
            )

        max_start = self.length - shard_len
        start_idx = random.randint(0, max_start)
        end_idx = start_idx + shard_len

        shard = self.df.iloc[start_idx:end_idx].copy()
        shard.reset_index(drop=True, inplace=True)
        return shard

    # ----------------------------------------------------------------------
    # Convenience access
    # ----------------------------------------------------------------------
    def get_row(self, i: int):
        """Return row i as dict (device-friendly)."""
        if i < 0 or i >= self.length:
            raise IndexError("Index out of range.")
        return self.df.iloc[i].to_dict()

    def __len__(self):
        return self.length

    # ----------------------------------------------------------------------
    # Demo plotting
    # ----------------------------------------------------------------------
    def main_demo(self, num_shards: int = 3, shard_len: int = 500):
        """
        Plots several shards and some global metrics for quick inspection.

        - Histograms of full dataset pressure, vibration, humidity
        - num_shards random shards of length shard_len
        """
        print("\n[IndustrialDatasetReader] Running demo plotting...")

        # ==================================================================
        # 1. Full dataset distributions
        # ==================================================================
        plt.figure(figsize=(10, 4))
        plt.hist(self.df["pressure"], bins=40)
        plt.title("Distribution of Pressure")
        plt.xlabel("Pressure")
        plt.ylabel("Count")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        plt.figure(figsize=(10, 4))
        plt.hist(self.df["vibration"], bins=40)
        plt.title("Distribution of Vibration")
        plt.xlabel("Vibration")
        plt.ylabel("Count")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        plt.figure(figsize=(10, 4))
        plt.hist(self.df["humidity"], bins=40)
        plt.title("Distribution of Humidity")
        plt.xlabel("Humidity")
        plt.ylabel("Count")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        # ==================================================================
        # 2. Shard plots
        # ==================================================================
        for i in range(num_shards):
            shard = self.get_shard(shard_len)
            print(f"[Demo] Shard {i+1}: {len(shard)} rows")

            x = range(len(shard))

            plt.figure(figsize=(12, 5))
            plt.plot(x, shard["pressure"], label="Pressure", linewidth=2)
            plt.plot(x, shard["vibration"], label="Vibration", alpha=0.8)
            plt.plot(x, shard["humidity"], label="Humidity", alpha=0.8)

            plt.title(f"Shard {i+1} — Pressure, Vibration, Humidity vs sample index")
            plt.xlabel("Sample index (synthetic time step)")
            plt.ylabel("Sensor values")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()

        print("[IndustrialDatasetReader] Demo completed.\n")


if __name__ == "__main__":
    reader = IndustrialDatasetReader("datasets/chicago.csv")
    reader.main_demo(num_shards=3, shard_len=500)
