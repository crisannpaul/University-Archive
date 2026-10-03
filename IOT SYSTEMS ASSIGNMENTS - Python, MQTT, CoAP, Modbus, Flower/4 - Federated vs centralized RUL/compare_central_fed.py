# run_compare_central_vs_fed.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch

# Centralized pieces
from data_windows import make_centralized_loaders, make_federated_loaders
from model_lstm import LSTMConfig, LSTMRegressor
from training import TrainConfig, train_model
from plotting import load_history, plot_histories, plot_compare_all_splits

# Federated (Flower) pieces
try:
    import flwr as fl
except ImportError as e:
    raise SystemExit("Flower is not installed. Run: pip install flwr[simulation]") from e

from fl_client import CmapssClient, set_parameters
from training import evaluate


def weighted_avg(metrics: List[Tuple[int, Dict]]) -> Dict:
    """Weighted average of client metrics for a round."""
    total = sum(num_examples for num_examples, _ in metrics)
    if total == 0:
        return {}
    out: Dict[str, float] = {}
    for num_examples, m in metrics:
        w = num_examples / total
        for k, v in m.items():
            out[k] = out.get(k, 0.0) + w * float(v)
    return out


def history_to_rows(hist: fl.server.history.History) -> List[Dict]:
    """
    Convert Flower History to 'epoch-style' dicts:
      {'epoch': round, 'train_rmse':..., 'val_rmse':..., 'test_rmse':...}
    so we can reuse existing plotting.
    """
    centralized = hist.metrics_centralized or {}
    rounds = set()
    for _, pairs in centralized.items():
        for r, _ in pairs:
            rounds.add(r)

    rows: Dict[int, Dict] = {int(r): {"epoch": int(r)} for r in rounds}
    for k, pairs in centralized.items():
        for r, val in pairs:
            rows[int(r)][k] = float(val)

    dist_fit = hist.metrics_distributed_fit or {}
    for k, pairs in dist_fit.items():
        for r, val in pairs:
            rows.setdefault(int(r), {"epoch": int(r)})[k] = float(val)

    return [rows[r] for r in sorted(rows.keys())]


def main():
    # ------------------- EDIT THESE -------------------
    root = Path("Dataset")     # folder containing train_FD00x.txt etc
    dataset_id = "FD001"       # FD001/FD002/FD003/FD004
    # --------------------------------------------------

    # Shared "sweet spot"
    seq_len = 50
    batch_size = 128
    val_ratio = 0.1

    # Centralized training hyperparams
    central_epochs = 20
    central_lr = 1e-3
    central_patience = 8

    # Federated hyperparams
    num_clients = 10
    num_rounds = 20
    fraction_fit = 1.0         # since only 10 clients; set 0.5 if you want 5/round
    local_epochs = 1
    fed_lr = 1e-3

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("Device:", device)

    out_dir = Path("runs") / f"compare_{dataset_id}_sl{seq_len}_bs{batch_size}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # ==================================================
    # 1) CENTRALIZED
    # ==================================================
    print("\n=== CENTRALIZED ===")
    loaders = make_centralized_loaders(
        root_dir=root,
        dataset_id=dataset_id,
        seq_len=seq_len,
        stride=1,
        batch_size=batch_size,
        val_ratio=val_ratio,
        seed=42,
        eval_last_window_only=True,
    )

    num_features = loaders["meta"]["num_features"]
    print("Num features:", num_features)

    central_model = LSTMRegressor(
        LSTMConfig(input_size=num_features, hidden_size=64, num_layers=2, dropout=0.1)
    )

    central_cfg = TrainConfig(
        epochs=central_epochs,
        lr=central_lr,
        device=device,
        out_dir=str(out_dir),
        run_name="centralized",
        patience=central_patience,
        monitor="val_rmse",
        mode="min",
        save_best=True,
        seed=42,
        show_progress=True,
        print_every_epoch=True,
    )

    # NOTE: this assumes you updated train_model to accept test_loader (as we patched earlier)
    central_result = train_model(
        central_model,
        loaders["train"],
        loaders["val"],
        loaders["test"],      # logs test metrics each epoch (eval-only, no gradients)
        central_cfg,
    )
    central_hist = load_history(central_result["paths"]["history"])

    # Copy centralized history to compare folder root
    (out_dir / "centralized_history.json").write_text(json.dumps(central_hist, indent=2), encoding="utf-8")

    # ==================================================
    # 2) FEDERATED (FedAvg)
    # ==================================================
    print("\n=== FEDERATED (FedAvg) ===")
    fed = make_federated_loaders(
        root_dir=root,
        dataset_id=dataset_id,
        num_clients=num_clients,
        seq_len=seq_len,
        batch_size=batch_size,
        val_ratio=val_ratio,
        seed=42,
        eval_last_window_only=True,
    )

    client_loaders = fed["client_loaders"]
    val_loader = fed["val_loader"]
    test_loader = fed["test_loader"]
    meta = fed["meta"]

    print("Fed clients:", meta["num_clients"], "| Features:", meta["num_features"])

    def make_model():
        return LSTMRegressor(
            LSTMConfig(input_size=meta["num_features"], hidden_size=64, num_layers=2, dropout=0.1)
        )

    server_model = make_model().to(device)

    def evaluate_fn(server_round: int, parameters, config):
        set_parameters(server_model, parameters)

        val_loss, val_m = evaluate(server_model, val_loader, torch.device(device), show_pbar=False)
        test_loss, test_m = evaluate(server_model, test_loader, torch.device(device), show_pbar=False)

        return float(val_loss), {
            "val_rmse": float(val_m["rmse"]),
            "test_rmse": float(test_m["rmse"]),
            "val_mae": float(val_m["mae"]),
            "test_mae": float(test_m["mae"]),
        }

    def client_fn(cid: str):
        cid_int = int(cid)
        model = make_model()
        return CmapssClient(
            model=model,
            train_loader=client_loaders[cid_int],
            device=device,
            lr=fed_lr,
            local_epochs=local_epochs,
            grad_clip_norm=1.0,
        )

    strategy = fl.server.strategy.FedAvg(
        fraction_fit=fraction_fit,
        min_fit_clients=int(np.ceil(num_clients * fraction_fit)),
        min_available_clients=num_clients,
        evaluate_fn=evaluate_fn,
        fit_metrics_aggregation_fn=weighted_avg,
        on_fit_config_fn=lambda r: {"local_epochs": local_epochs, "lr": fed_lr},
    )

    hist = fl.simulation.start_simulation(
        client_fn=client_fn,
        num_clients=num_clients,
        config=fl.server.ServerConfig(num_rounds=num_rounds),
        strategy=strategy,
        client_resources={"num_cpus": 1},
    )

    fed_rows = history_to_rows(hist)
    (out_dir / "federated_history.json").write_text(json.dumps(fed_rows, indent=2), encoding="utf-8")

    # ==================================================
    # 3) COMPARISON PLOTS (same plots, two lines)
    # ==================================================
    # NOTE: centralized x-axis = epochs, federated x-axis = rounds.
    # We still plot them together; interpret as "training progress steps".
    print("\n=== PLOTTING COMPARISONS ===")
    plot_histories(
        [central_hist, fed_rows],
        ["centralized", "federated"],
        key="train_rmse",
        save_path=out_dir / "compare_train_rmse.png",
        show=False,
        title="Train RMSE (centralized vs federated)",
    )
    plot_histories(
        [central_hist, fed_rows],
        ["centralized", "federated"],
        key="val_rmse",
        save_path=out_dir / "compare_val_rmse.png",
        show=False,
        title="Val RMSE (centralized vs federated)",
    )
    plot_histories(
        [central_hist, fed_rows],
        ["centralized", "federated"],
        key="test_rmse",
        save_path=out_dir / "compare_test_rmse.png",
        show=False,
        title="Test RMSE (centralized vs federated)",
    )

    plot_compare_all_splits(
        central_hist,
        fed_rows,
        metric="rmse",
        save_path=out_dir / "compare_all_rmse_one_plot.png",
        show=False,
    )


    print("Saved outputs to:", out_dir)


if __name__ == "__main__":
    main()
