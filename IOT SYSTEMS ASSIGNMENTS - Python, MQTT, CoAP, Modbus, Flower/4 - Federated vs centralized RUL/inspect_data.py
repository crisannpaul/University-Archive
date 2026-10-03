# inspect_data.py
from __future__ import annotations

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from data_cmapss import load_split, basic_inspection


SENSOR_COLS = [f"s{i}" for i in range(1, 22)]
OS_COLS = ["os1", "os2", "os3"]


def _missing_report(df):
    nan_counts = df.isna().sum()
    total_nans = int(nan_counts.sum())

    num_df = df.select_dtypes(include=["number"])
    inf_mask = np.isinf(num_df.to_numpy())
    total_infs = int(inf_mask.sum())

    return {
        "total_nans": total_nans,
        "cols_with_nans": nan_counts[nan_counts > 0].to_dict(),
        "total_infs": total_infs,
    }


def _rows_per_unit(df):
    return df.groupby("unit").size().sort_values()


def _print_split(name: str, df):
    info = basic_inspection(df)
    miss = _missing_report(df)

    print(f"\n=== {name} ===")
    print(f"Engines (units): {info['num_units']}")
    print(f"Total rows:      {info['total_rows']}")
    print(
        f"Rows/engine:     min={info['min_rows_per_unit']}  "
        f"median={info['median_rows_per_unit']:.1f}  "
        f"mean={info['mean_rows_per_unit']:.1f}  "
        f"max={info['max_rows_per_unit']}"
    )

    print(f"Missing values:  total_nans={miss['total_nans']} | total_infs={miss['total_infs']}")
    if miss["cols_with_nans"]:
        print("Columns with NaNs:", miss["cols_with_nans"])


# -------------------------
# RUL labeling for plots
# -------------------------

def add_rul_train(train_df):
    df = train_df.copy()
    max_cycle = df.groupby("unit")["cycle"].max()
    df["rul"] = (max_cycle[df["unit"]].to_numpy() - df["cycle"].to_numpy()).astype(np.float32)
    return df


def add_rul_test(test_df, rul_vec: np.ndarray):
    df = test_df.copy()
    last_cycle = df.groupby("unit")["cycle"].max().sort_index()
    units = last_cycle.index.to_numpy()

    if len(rul_vec) != len(units):
        raise ValueError(f"RUL length ({len(rul_vec)}) != #test units ({len(units)})")

    rul_last_by_unit = {int(u): float(r) for u, r in zip(units, rul_vec)}
    # RUL(t) = RUL_last + (last_cycle - cycle)
    df["rul"] = df.apply(
        lambda row: rul_last_by_unit[int(row["unit"])] + (last_cycle[int(row["unit"])] - row["cycle"]),
        axis=1,
    ).astype(np.float32)
    return df


# -------------------------
# Visualizations
# -------------------------

def plot_rul_vs_cycles(df_unit, out_path: Path, title: str):
    cycles = df_unit["cycle"].to_numpy()
    rul = df_unit["rul"].to_numpy()

    plt.figure()
    plt.plot(cycles, rul)
    plt.xlabel("Cycle")
    plt.ylabel("RUL")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, bbox_inches="tight", dpi=160)
    plt.close()


def plot_sensor_trends_per_engine(df_unit, out_path: Path, title: str, top_k: int = 6):
    """
    Plot top_k sensors (by variance within this engine) over cycles.
    To make multiple sensors comparable on one plot, we z-score per sensor within this engine.
    """
    cycles = df_unit["cycle"].to_numpy()

    # choose sensors with highest variance for THIS engine
    variances = df_unit[SENSOR_COLS].var().sort_values(ascending=False)
    chosen = list(variances.head(top_k).index)

    # z-score per sensor to compare trends
    X = df_unit[chosen].to_numpy(dtype=np.float32)
    mu = X.mean(axis=0, keepdims=True)
    sd = X.std(axis=0, keepdims=True)
    sd[sd == 0] = 1.0
    Xz = (X - mu) / sd

    plt.figure()
    for j, s in enumerate(chosen):
        plt.plot(cycles, Xz[:, j], label=s)

    plt.xlabel("Cycle")
    plt.ylabel("Sensor (z-scored per engine)")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.legend(loc="best", fontsize=8)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, bbox_inches="tight", dpi=160)
    plt.close()


def choose_representative_units(train_df):
    """
    Pick 3 train engines: shortest, median, longest trajectory.
    """
    counts = _rows_per_unit(train_df)  # sorted by length
    if len(counts) == 0:
        return []
    u_min = int(counts.index[0])
    u_max = int(counts.index[-1])
    u_med = int(counts.index[len(counts) // 2])
    # ensure unique order
    units = []
    for u in [u_min, u_med, u_max]:
        if u not in units:
            units.append(u)
    return units


def main():
    root = Path("Dataset")  # folder containing train_FD00x.txt/test_FD00x.txt/RUL_FD00x.txt
    out_root = Path("visuals")
    out_root.mkdir(parents=True, exist_ok=True)

    for dataset in ["FD001", "FD002", "FD003", "FD004"]:
        print("\n" + "=" * 60)
        print(f"Dataset: {dataset}")

        train_df, test_df, rul_vec = load_split(root, dataset)

        print(
            f"Train units: {train_df['unit'].nunique()} | "
            f"Test units: {test_df['unit'].nunique()} | "
            f"RUL length: {len(rul_vec)}"
        )
        if test_df["unit"].nunique() != len(rul_vec):
            print("WARNING: RUL length != # test units (check files).")

        _print_split("TRAIN", train_df)
        _print_split("TEST", test_df)

        # Add RUL columns just for visualization
        train_plot = add_rul_train(train_df)
        test_plot = add_rul_test(test_df, rul_vec)

        # Pick a few engines to visualize (train engines)
        units = choose_representative_units(train_df)
        print("Representative train units for plots:", units)

        ds_out = out_root / dataset
        ds_out.mkdir(parents=True, exist_ok=True)

        for u in units:
            dfu = train_plot[train_plot["unit"] == u].sort_values("cycle")

            plot_sensor_trends_per_engine(
                dfu,
                ds_out / f"train_unit{u}_sensor_trends.png",
                title=f"{dataset} TRAIN unit {u}: sensor trends (top variance sensors)",
                top_k=6,
            )
            plot_rul_vs_cycles(
                dfu,
                ds_out / f"train_unit{u}_rul_vs_cycles.png",
                title=f"{dataset} TRAIN unit {u}: RUL vs cycles",
            )

        # Also do 1 test engine example (unit 1 if it exists, else smallest)
        test_units = sorted(test_plot["unit"].unique().tolist())
        if test_units:
            u_test = test_units[0]
            dfu_test = test_plot[test_plot["unit"] == u_test].sort_values("cycle")

            plot_sensor_trends_per_engine(
                dfu_test,
                ds_out / f"test_unit{u_test}_sensor_trends.png",
                title=f"{dataset} TEST unit {u_test}: sensor trends (top variance sensors)",
                top_k=6,
            )
            plot_rul_vs_cycles(
                dfu_test,
                ds_out / f"test_unit{u_test}_rul_vs_cycles.png",
                title=f"{dataset} TEST unit {u_test}: RUL vs cycles",
            )

        print(f"Saved plots to: {ds_out.resolve()}")


if __name__ == "__main__":
    main()
