# analyze_runs.py
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import matplotlib.pyplot as plt


# ---------- IO helpers ----------
def _find_csv(path: Path, candidates: List[str]) -> Optional[Path]:
    for c in candidates:
        p = path / c
        if p.exists():
            return p
        for g in path.glob(c):
            return g
    return None


def _read_csv(p: Path, force_protocol: Optional[str] = None) -> Optional[pd.DataFrame]:
    try:
        df = pd.read_csv(p)
        needed = {"device_id", "timestamp", "sensor", "value"}
        missing = needed - set(df.columns)
        if missing:
            print(f"[WARN] {p} missing {missing}, skipping.")
            return None
        # Parse time & value
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna(subset=["timestamp", "value"]).sort_values("timestamp").reset_index(drop=True)
        # Protocol
        if "protocol" not in df.columns or force_protocol:
            df["protocol"] = force_protocol or "unknown"
        # Derive sensor from device_id (e.g., temperature_0)
        df["sensor_from_id"] = df["device_id"].astype(str).str.split("_").str[0]
        # If sensor column differs, trust the device_id prefix (keeps grouping consistent)
        mism = (df["sensor"].astype(str) != df["sensor_from_id"])
        if mism.any():
            df.loc[mism, "sensor"] = df.loc[mism, "sensor_from_id"]
        df.drop(columns=["sensor_from_id"], inplace=True)
        # Canonical types
        df["sensor"] = df["sensor"].astype(str)
        df["device_id"] = df["device_id"].astype(str)
        return df
    except Exception as e:
        print(f"[WARN] Failed to read {p}: {e}")
        return None


def _load_run(run_dir: Path) -> pd.DataFrame:
    http_p = _find_csv(run_dir, ["readings_http.csv", "reading_http.csv", "*http*.csv"])
    mqtt_p = _find_csv(run_dir, ["readings_mqtt.csv", "reading_mqtt.csv", "reading_mqtt.cvs", "*mqtt*.csv", "*mqtt*.cvs"])
    dfs = []
    if http_p:
        d = _read_csv(http_p, force_protocol="http")
        if d is not None: dfs.append(d)
    if mqtt_p:
        d = _read_csv(mqtt_p, force_protocol="mqtt")
        if d is not None: dfs.append(d)
    if not dfs:
        return pd.DataFrame(columns=["device_id","protocol","timestamp","sensor","value"])
    return pd.concat(dfs, ignore_index=True)


def _ensure_dir(p: Path): p.mkdir(parents=True, exist_ok=True)
def _savefig(path: Path): plt.tight_layout(); plt.savefig(path, dpi=140); plt.close()


# ---------- Plotting ----------
def plot_timeseries_two_devices_per_sensor(df: pd.DataFrame, out_dir: Path, protocol: Optional[str] = None):
    """For each sensor, pick top-2 devices (by message count) and overlay their time-series."""
    if protocol:
        data = df[df["protocol"] == protocol].copy()
        label = protocol.upper()
    else:
        data = df.copy()
        label = "ALL"

    if data.empty: 
        print(f"[INFO] No data for {label} time-series."); 
        return

    for sensor, g in data.groupby("sensor"):
        # pick top 2 device_ids by number of rows
        top_devices = g["device_id"].value_counts().head(2).index.tolist()
        if not top_devices:
            continue
        plt.figure(figsize=(10,4))
        for dev in top_devices:
            s = g[g["device_id"] == dev]
            if s.empty: 
                continue
            plt.plot(s["timestamp"], s["value"], label=dev)
        plt.title(f"{label} time-series — sensor: {sensor} (top 2 devices)")
        plt.xlabel("time"); plt.ylabel("value"); plt.legend()
        _savefig(out_dir / f"{label.lower()}_timeseries_{sensor}_top2.png")


def plot_messages_per_minute(df: pd.DataFrame, out_dir: Path):
    if df.empty: return
    dti = df.set_index("timestamp")
    # total
    per_min = dti["value"].resample("1min").count()
    plt.figure(figsize=(10,4)); plt.plot(per_min.index, per_min.values)
    plt.title("Messages per minute — total (HTTP+MQTT)"); plt.xlabel("time"); plt.ylabel("count")
    _savefig(out_dir / "messages_per_minute_total.png")
    # split
    for proto, g in dti.groupby("protocol"):
        pm = g["value"].resample("1min").count()
        plt.figure(figsize=(10,4)); plt.plot(pm.index, pm.values)
        plt.title(f"Messages per minute — {proto.upper()}"); plt.xlabel("time"); plt.ylabel("count")
        _savefig(out_dir / f"messages_per_minute_{proto}.png")


def plot_cumulative_messages(df: pd.DataFrame, out_dir: Path):
    if df.empty: return
    d = df.sort_values("timestamp").copy()
    d["one"] = 1
    d["cum"] = d["one"].cumsum()
    plt.figure(figsize=(10,4)); plt.plot(d["timestamp"], d["cum"])
    plt.title("Cumulative messages — total (HTTP+MQTT)"); plt.xlabel("time"); plt.ylabel("cumulative count")
    _savefig(out_dir / "cumulative_messages_total.png")
    for proto, g in d.groupby("protocol"):
        g = g.copy(); g["one"] = 1; g["cum"] = g["one"].cumsum()
        plt.figure(figsize=(10,4)); plt.plot(g["timestamp"], g["cum"])
        plt.title(f"Cumulative messages — {proto.upper()}"); plt.xlabel("time"); plt.ylabel("cumulative count")
        _savefig(out_dir / f"cumulative_messages_{proto}.png")


def plot_sensor_avg_over_time(df: pd.DataFrame, out_dir: Path, rule="3s"):
    """Average value per sensor over time (resampled window ~ your device period)."""
    if df.empty: return
    d = df.set_index("timestamp")
    for sensor, g in d.groupby("sensor"):
        series = g["value"].resample(rule).mean()
        if series.dropna().empty: 
            continue
        plt.figure(figsize=(10,4)); plt.plot(series.index, series.values)
        plt.title(f"Average value over time — {sensor} (resample {rule})")
        plt.xlabel("time"); plt.ylabel("avg value")
        _savefig(out_dir / f"avg_value_timeseries_{sensor}.png")


def cross_run_volume_comparison(run_dfs: Dict[str,pd.DataFrame], out_dir: Path):
    plt.figure(figsize=(10,4))
    plotted = False
    for name, df in run_dfs.items():
        if df.empty: 
            continue
        pm = df.set_index("timestamp")["value"].resample("1min").count()
        if pm.empty:
            continue
        plt.plot(pm.index, pm.values, label=name); plotted = True
    if not plotted:
        plt.close(); return
    plt.title("Messages per minute — comparison across runs"); plt.xlabel("time"); plt.ylabel("count"); plt.legend()
    _savefig(out_dir / "messages_per_minute_comparison.png")


# ---------- Main ----------
def analyze_run(run_dir: Path) -> pd.DataFrame:
    df = _load_run(run_dir)
    if df.empty:
        print(f"[WARN] No data in {run_dir}")
        return df
    # Save plots inside the same folder
    _ensure_dir(run_dir)

    # Per-sensor, top-2 devices overlay — BOTH (ALL), HTTP, MQTT
    plot_timeseries_two_devices_per_sensor(df, run_dir, protocol=None)
    plot_timeseries_two_devices_per_sensor(df, run_dir, protocol="http")
    plot_timeseries_two_devices_per_sensor(df, run_dir, protocol="mqtt")

    # Volume & cumulative
    plot_messages_per_minute(df, run_dir)
    plot_cumulative_messages(df, run_dir)

    # Sensor averages (resampled ~3s)
    plot_sensor_avg_over_time(df, run_dir, rule="3s")

    print(f"[OK] Saved plots for {run_dir}")
    return df


def main():
    ap = argparse.ArgumentParser(description="Create plots from IoT simulation CSV outputs.")
    ap.add_argument("--outdir", default="out", help="Base output directory containing run folders")
    ap.add_argument("--runs", default="4devices,40devices", help="Comma-separated run folders under outdir")
    args = ap.parse_args()

    base = Path(args.outdir)
    run_names = [r.strip() for r in args.runs.split(",") if r.strip()]
    run_dfs: Dict[str, pd.DataFrame] = {}

    for rn in run_names:
        rd = base / rn
        if not rd.exists():
            print(f"[WARN] Missing run folder: {rd}")
            continue
        run_dfs[rn] = analyze_run(rd)

    # Cross-run comparison saved to base folder
    _ensure_dir(base)
    cross_run_volume_comparison(run_dfs, base)
    print(f"[DONE] Cross-run comparison saved to {base}")


if __name__ == "__main__":
    main()
