import pandas as pd
import numpy as np
import random
from pathlib import Path
import matplotlib.pyplot as plt


class AirQualityDatasetReader:
    """
    Reader + preprocessor for the UCI Air Quality dataset.
    Used for MQTT device data sourcing.

    Behavior:
      - Loads dataset
      - Keeps only: T (Temperature), CO(GT)
      - Handles missing values (-200 and NaN) via forward/backward fill
      - Provides fixed-length shards for simulated devices:
            random start index (inside valid range)
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

        # UCI Air Quality uses ';' as separator and ',' as decimal
        # We only care about T and CO(GT)
        self.df = pd.read_csv(
            self.path,
            sep=';',
            decimal=',',
            usecols=["T", "CO(GT)"],
            engine="python",
        )
        print(f"[AirQualityDatasetReader] Loaded dataset with {len(self.df)} rows.")

    def _preprocess(self):
        """Fixes missing values and keeps only the needed numeric columns."""
        # Replace sentinel -200 and other invalids with NaN
        self.df["T"] = self.df["T"].replace(-200, np.nan)
        self.df["CO(GT)"] = self.df["CO(GT)"].replace(-200, np.nan)

        # Forward and backward fill both columns
        self.df["T"] = self.df["T"].ffill().bfill()
        self.df["CO(GT)"] = self.df["CO(GT)"].ffill().bfill()

        # Drop any remaining NaNs just in case
        self.df.dropna(subset=["T", "CO(GT)"], inplace=True)

        # Reset index and compute length
        self.df.reset_index(drop=True, inplace=True)
        self.length = len(self.df)
        print(f"[AirQualityDatasetReader] Preprocessed dataset, final rows: {self.length}")

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

        # Choose start so that [start, start + shard_len) is within the dataset
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

        - Histograms of full dataset T and CO(GT)
        - num_shards random shards of length shard_len
        """
        print("\n[AirQualityDatasetReader] Running demo plotting...")

        # ==================================================================
        # 1. Plot full dataset distribution
        # ==================================================================
        plt.figure(figsize=(10, 4))
        plt.hist(self.df["T"], bins=40)
        plt.title("Distribution of Temperature (T)")
        plt.xlabel("Temperature (°C)")
        plt.ylabel("Count")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        plt.figure(figsize=(10, 4))
        plt.hist(self.df["CO(GT)"], bins=40)
        plt.title("Distribution of CO(GT)")
        plt.xlabel("CO concentration")
        plt.ylabel("Count")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        # ==================================================================
        # 2. Plot shards (index-based, since timestamps are synthetic later)
        # ==================================================================
        for i in range(num_shards):
            shard = self.get_shard(shard_len)
            print(f"[Demo] Shard {i+1}: {len(shard)} rows")

            x = range(len(shard))

            plt.figure(figsize=(12, 5))
            plt.plot(x, shard["T"], label="Temperature (T)", linewidth=2)
            plt.plot(x, shard["CO(GT)"], label="CO(GT)", alpha=0.7)

            plt.title(f"Shard {i+1} — T & CO(GT) vs sample index")
            plt.xlabel("Sample index (synthetic time step)")
            plt.ylabel("Sensor values")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()

        print("[AirQualityDatasetReader] Demo completed.\n")


if __name__ == "__main__":
    reader = AirQualityDatasetReader("datasets/AirQuality.csv")
    reader.main_demo(num_shards=3, shard_len=500)
