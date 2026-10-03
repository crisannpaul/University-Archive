# run_federated.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import flwr as fl
import numpy as np
import torch

from data_windows import make_federated_loaders
from fl_client import CmapssClient, set_parameters, get_parameters
from model_lstm import LSTMConfig, LSTMRegressor
from training import evaluate
from plotting import plot_histories, plot_train_val_test


def weighted_avg(metrics: List[Tuple[int, Dict]]) -> Dict:
    """Weighted average of client metrics for a round."""
    total = sum(num_examples for num_examples, _ in metrics)
    if total == 0:
        return {}
    out = {}
    for num_examples, m in metrics:
        w = num_examples / total
        for k, v in m.items():
            out[k] = out.get(k, 0.0) + w * float(v)
    return out


def history_to_rows(hist: fl.server.history.History) -> List[Dict]:
    """
    Convert Flower History to the same "epoch-style" rows you already plot.
    We'll store round as epoch for reusing plotting code.
    """
    # centralized evaluation metrics (server evaluate_fn)
    centralized = hist.metrics_centralized or {}
    rounds = set()

    for k, pairs in centralized.items():
        for r, _ in pairs:
            rounds.add(r)

    rows = []
    for r in sorted(rounds):
        row = {"epoch": int(r)}
        # attach all centralized metrics for that round
        for k, pairs in centralized.items():
            for rr, val in pairs:
                if rr == r:
                    row[k] = float(val)
        rows.append(row)

    # distributed fit metrics (client-side train metrics aggregated)
    dist_fit = hist.metrics_distributed_fit or {}
    # dist_fit[k] = [(round, value), ...]
    # merge into rows
    by_round = {row["epoch"]: row for row in rows}
    for k, pairs in dist_fit.items():
        for r, val in pairs:
            by_round.setdefault(int(r), {"epoch": int(r)})[k] = float(val)

    return [by_round[r] for r in sorted(by_round)]


def main():
    # ---- EDIT THIS ----
    root = Path("Dataset")
    dataset_id = "FD001"   # change if needed
    # -------------------

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Your sweet spot
    seq_len = 50
    batch_size = 128
    num_clients = 10

    # FL hyperparams
    num_rounds = 20
    fraction_fit = 1.0          # since only 10 clients; you can set 0.5 etc.
    local_epochs = 1
    lr = 1e-3

    fed = make_federated_loaders(
        root_dir=root,
        dataset_id=dataset_id,
        num_clients=num_clients,
        seq_len=seq_len,
        batch_size=batch_size,
        val_ratio=0.1,
        seed=42,
        eval_last_window_only=True,
    )

    client_loaders = fed["client_loaders"]
    val_loader = fed["val_loader"]
    test_loader = fed["test_loader"]
    meta = fed["meta"]

    print("Federated meta:", {k: meta[k] for k in ["num_clients", "num_features", "early_rul", "dataset_id", "seq_len", "batch_size"]})
    print("Dropped constant cols:", meta["dropped_constant_cols"])

    # Global model factory
    def make_model():
        return LSTMRegressor(
            LSTMConfig(
                input_size=meta["num_features"],
                hidden_size=64,
                num_layers=2,
                dropout=0.1,
            )
        )

    # Server-side evaluation: compute val_rmse + test_rmse each round (no weight updates here)
    server_model = make_model().to(device)

    def evaluate_fn(server_round: int, parameters, config):
        set_parameters(server_model, parameters)

        val_loss, val_m = evaluate(server_model, val_loader, torch.device(device), show_pbar=False)
        test_loss, test_m = evaluate(server_model, test_loader, torch.device(device), show_pbar=False)

        # Return a loss (Flower expects one) + metrics dict
        # We'll return VAL loss, and log both val/test metrics.
        return float(val_loss), {
            "val_rmse": float(val_m["rmse"]),
            "val_mae": float(val_m["mae"]),
            "test_rmse": float(test_m["rmse"]),
            "test_mae": float(test_m["mae"]),
        }

    # Client function
    def client_fn(cid: str):
        cid_int = int(cid)
        model = make_model()
        return CmapssClient(
            model=model,
            train_loader=client_loaders[cid_int],
            device=device,
            lr=lr,
            local_epochs=local_epochs,
            grad_clip_norm=1.0,
        )

    # Strategy
    strategy = fl.server.strategy.FedAvg(
        fraction_fit=fraction_fit,
        min_fit_clients=num_clients,
        min_available_clients=num_clients,
        evaluate_fn=evaluate_fn,
        fit_metrics_aggregation_fn=weighted_avg,
    )

    # Run simulation
    hist = fl.simulation.start_simulation(
        client_fn=client_fn,
        num_clients=num_clients,
        config=fl.server.ServerConfig(num_rounds=num_rounds),
        strategy=strategy,
        client_resources={"num_cpus": 1},
    )

    # Save run
    out_dir = Path("runs") / f"federated_{dataset_id}_c{num_clients}_sl{seq_len}"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = history_to_rows(hist)
    history_path = out_dir / "history.json"
    history_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("Saved:", history_path)

    # Plots: separate + combined (RMSE)
    plot_histories([rows], ["fedavg"], key="train_rmse", save_path=out_dir / "train_rmse.png", show=False)
    plot_histories([rows], ["fedavg"], key="val_rmse", save_path=out_dir / "val_rmse.png", show=False)
    plot_histories([rows], ["fedavg"], key="test_rmse", save_path=out_dir / "test_rmse.png", show=False)
    plot_train_val_test(rows, metric="rmse", save_path=out_dir / "rmse_train_val_test.png", show=False)

    print("Done. Check plots in:", out_dir)


if __name__ == "__main__":
    main()
