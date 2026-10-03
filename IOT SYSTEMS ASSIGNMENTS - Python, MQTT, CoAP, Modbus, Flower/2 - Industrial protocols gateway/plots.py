# plots.py
from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt


# -----------------------------------------------------------
# Helpers
# -----------------------------------------------------------
def parse_ts(s: str):
    """
    Robust ISO8601 parser that handles:
      - 2025-11-23T14:32:03Z
      - 2025-11-23T14:32:03.175833+00:00
    """
    if not isinstance(s, str):
        return None
    s = s.strip()
    if not s:
        return None
    # Normalize trailing 'Z' to '+00:00'
    if s.endswith("Z") and "+" not in s:
        s = s[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def load_data(csv_path: str = "gateway_output.csv") -> pd.DataFrame:
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"{csv_path} not found")

    df = pd.read_csv(csv_path)

    print("Columns:", df.columns.tolist())
    print("Protocol counts:\n", df["protocol"].value_counts(), "\n")

    required = [
        "device_id",
        "protocol",
        "produced_timestamp",
        "delivered_timestamp",
        "sensor",
        "value",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit(f"Missing columns in CSV: {missing}")

    return df


# -----------------------------------------------------------
# Plot 1: Latency per protocol
# -----------------------------------------------------------
def plot_latency(df: pd.DataFrame, plots_dir: Path):
    # Compute latency manually using datetime.fromisoformat
    def compute_latency(row):
        prod = parse_ts(row["produced_timestamp"])
        dev = parse_ts(row["delivered_timestamp"])
        if prod is None or dev is None:
            return None
        return (dev - prod).total_seconds()

    df = df.copy()
    df["latency_s"] = df.apply(compute_latency, axis=1)

    # Keep only valid, non-negative latencies
    df = df.dropna(subset=["latency_s"])
    df = df[df["latency_s"] >= 0]

    if df.empty:
        print("[Latency] No valid rows with latency to plot.")
        return

    # Debug: show stats per protocol
    for proto in df["protocol"].unique():
        sub = df[df["protocol"] == proto]
        print(f"\n[Latency] Protocol: {proto}")
        print(
            sub[
                [
                    "device_id",
                    "produced_timestamp",
                    "delivered_timestamp",
                    "latency_s",
                ]
            ].head(5)
        )
        print("Latency stats (seconds):")
        print(sub["latency_s"].describe())

    # Average latency per protocol
    latency_stats = df.groupby("protocol")["latency_s"].mean()
    print("\n[Latency] Average latency per protocol (seconds):")
    print(latency_stats.round(4))

    # Plot
    plt.figure(figsize=(8, 5))
    plt.bar(latency_stats.index, latency_stats.values)
    plt.ylabel("Average latency (s)")
    plt.xlabel("Protocol")
    plt.title("Average Delivery Latency per Protocol")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()

    out_path = plots_dir / "latency_per_protocol.png"
    plt.savefig(out_path, dpi=150)
    plt.close()

    print(f"[Latency] Saved plot to: {out_path}")


# -----------------------------------------------------------
# Plot 2: Packet loss per protocol (value == -100)
# -----------------------------------------------------------
def plot_packet_loss(df: pd.DataFrame, plots_dir: Path):
    df = df.copy()

    # Ensure numeric so we can compare against the sentinel
    df["value_num"] = pd.to_numeric(df["value"], errors="coerce")

    # Same loss sentinel as used in BaseDevice / ModbusDevice
    LOSS_SENTINEL = 65534

    # Rows where we consider the packet "lost"
    loss_mask = df["value_num"] == LOSS_SENTINEL
    loss_df = df[loss_mask]

    if loss_df.empty:
        print("[PacketLoss] No lost packets (value == 65534) in data.")
        return

    # Count lost packets per protocol
    loss_counts = loss_df.groupby("protocol")["value_num"].count()
    print("\n[PacketLoss] Lost packet counts per protocol:")
    print(loss_counts)

    # Plot
    plt.figure(figsize=(8, 5))
    plt.bar(loss_counts.index, loss_counts.values)
    plt.ylabel("Count of lost packets (value == 65534)")
    plt.xlabel("Protocol")
    plt.title("Packet Loss per Protocol")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()

    out_path = plots_dir / "packet_loss_per_protocol.png"
    plt.savefig(out_path, dpi=150)
    plt.close()

    print(f"[PacketLoss] Saved plot to: {out_path}")

def plot_sensor_timeseries(df: pd.DataFrame, plots_dir: Path):
    """
    Plot each sensor's readings over time.
    One line per (protocol, sensor) combination, all on the same figure.

    Packet loss values (65534) are treated as NaN and forward-filled
    so the visual time series remains continuous.
    """
    df = df.copy()

    # Parse timestamps using the same robust parser
    df["t"] = df["produced_timestamp"].apply(parse_ts)
    df = df.dropna(subset=["t"])

    # Ensure numeric values
    df["value_num"] = pd.to_numeric(df["value"], errors="coerce")

    # Treat the loss sentinel as missing
    LOSS_SENTINEL = 65534
    df.loc[df["value_num"] == LOSS_SENTINEL, "value_num"] = pd.NA

    # Sort by time so forward-fill makes sense
    df = df.sort_values("t")

    # Forward-fill per (protocol, sensor) group
    df["value_ffill"] = (
        df.groupby(["protocol", "sensor"])["value_num"]
        .ffill()
    )

    # Drop rows where we still don't have a value after ffill (e.g. leading NaNs)
    df = df.dropna(subset=["value_ffill"])

    if df.empty:
        print("[Sensors] No valid readings to plot.")
        return

    # Create one big figure with all sensors
    plt.figure(figsize=(12, 6))

    # Group by protocol + sensor and plot each group
    for (proto, sensor), sub in df.groupby(["protocol", "sensor"]):
        if sub.empty:
            continue
        label = f"{sensor} ({proto})"
        plt.plot(
            sub["t"],
            sub["value_ffill"],
            marker=".",
            linestyle="-",
            alpha=0.7,
            label=label,
        )

    plt.xlabel("Produced timestamp")
    plt.ylabel("Sensor value (forward-filled on loss)")
    plt.title("Sensor readings over time by protocol & sensor")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="best")
    plt.tight_layout()

    out_path = plots_dir / "sensor_timeseries_all.png"
    plt.savefig(out_path, dpi=150)
    plt.close()

    print(f"[Sensors] Saved plot to: {out_path}")

def plot_latency_histograms(df: pd.DataFrame, plots_dir: Path):
    """
    Plot latency histograms for Modbus, MQTT, and CoAP
    using the same latency_s definition as in plot_latency.
    """
    df = df.copy()

    # Compute latency_s using the same robust parser
    def compute_latency(row):
        prod = parse_ts(row["produced_timestamp"])
        dev = parse_ts(row["delivered_timestamp"])
        if prod is None or dev is None:
            return None
        return (dev - prod).total_seconds()

    df["latency_s"] = df.apply(compute_latency, axis=1)

    # Valid, non-negative
    df = df.dropna(subset=["latency_s"])
    df = df[df["latency_s"] >= 0]

    if df.empty:
        print("[LatencyHist] No valid latencies to plot.")
        return

    protocols = ["modbus", "mqtt", "coap"]

    plt.figure(figsize=(12, 4))

    subplot_idx = 1
    for proto in protocols:
        sub = df[df["protocol"] == proto]
        if sub.empty:
            continue

        plt.subplot(1, 3, subplot_idx)
        subplot_idx += 1

        plt.hist(sub["latency_s"], bins=20, edgecolor="black", alpha=0.7)
        plt.title(f"{proto} latency")
        plt.xlabel("Latency (s)")
        plt.ylabel("Count")
        plt.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    out_path = plots_dir / "latency_histograms.png"
    plt.savefig(out_path, dpi=150)
    plt.close()

    print(f"[LatencyHist] Saved plot to: {out_path}")

def plot_pdr_vs_fault_probability(df: pd.DataFrame, plots_dir: Path):
    """
    For each device:
        - detect faults where gap > 2 sec
        - estimate sampling interval from median gap
        - estimate expected packets
        - compute PDR (delivered / expected)
        - plot PDR vs fault_probability
    """
    df = df.copy()
    df["t"] = df["produced_timestamp"].apply(parse_ts)
    df = df.dropna(subset=["t"])

    if df.empty:
        print("[PDR] No timestamp data.")
        return

    FAULT_GAP = 4.0  # seconds
    device_stats = []

    for device_id, sub in df.groupby("device_id"):
        sub = sub.sort_values("t")
        if len(sub) < 2:
            continue

        # Compute gaps
        sub["gap"] = sub["t"].diff().dt.total_seconds()

        valid_gaps = sub["gap"].dropna()
        if valid_gaps.empty:
            continue

        # Faults
        fault_gaps = valid_gaps[valid_gaps > FAULT_GAP]
        fault_probability = len(fault_gaps) / len(valid_gaps)

        # Estimate sampling interval from good gaps
        normal_gaps = valid_gaps[valid_gaps <= FAULT_GAP]
        if normal_gaps.empty:
            continue

        sampling_interval = normal_gaps.median()

        # Expected packets
        total_duration = (sub["t"].iloc[-1] - sub["t"].iloc[0]).total_seconds()
        expected_packets = max(1, int(total_duration / sampling_interval))

        delivered_packets = len(sub)
        pdr = delivered_packets / expected_packets

        device_stats.append({
            "device_id": device_id,
            "protocol": sub["protocol"].iloc[0],
            "fault_prob": fault_probability,
            "pdr": pdr
        })

    stats_df = pd.DataFrame(device_stats)
    if stats_df.empty:
        print("[PDR] No stats to plot.")
        return

    # --- Scatter plot ---
    plt.figure(figsize=(8, 6))
    for proto, group in stats_df.groupby("protocol"):
        plt.scatter(group["fault_prob"], group["pdr"], label=proto, s=80)

    plt.xlabel("Fault Probability")
    plt.ylabel("Packet Delivery Ratio (PDR)")
    plt.title("Packet Delivery Ratio vs Fault Probability")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()

    out = plots_dir / "pdr_vs_fault_probability.png"
    plt.savefig(out, dpi=150)
    plt.close()

    print(f"[PDR] Saved plot to: {out}")



# -----------------------------------------------------------
# Main
# -----------------------------------------------------------
def main():
    plots_dir = Path("plots")
    plots_dir.mkdir(parents=True, exist_ok=True)

    df = load_data("gateway_output.csv")

    # 1) Latency plot
    plot_latency(df, plots_dir)

    # 2) Packet loss plot (value == -100)
    plot_packet_loss(df, plots_dir)
    plot_sensor_timeseries(df, plots_dir)
    
    plot_latency_histograms(df, plots_dir)
    plot_pdr_vs_fault_probability(df, plots_dir)


if __name__ == "__main__":
    main()
