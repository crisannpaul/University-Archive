# run_centralized_fd001.py
from __future__ import annotations

from pathlib import Path

import torch

from data_windows import make_centralized_loaders
from model_lstm import LSTMConfig, LSTMRegressor
from training import TrainConfig, train_model, predict
from plotting import (
    load_history,
    plot_histories,
    plot_train_val_test,
    summary_regression,
    plot_pred_vs_true,
    plot_error_hist,
)



def main():
    # ---- EDIT THIS ----
    root = Path("Dataset")
    # -------------------

    # Data
    loaders = make_centralized_loaders(
        root_dir=root,
        dataset_id="FD003",
        seq_len=50,          # safe default given FD001 min engine length observed in your inspection
        stride=1,
        batch_size=128,
        val_ratio=0.1,
        seed=42,
        eval_last_window_only=True,
    )

    num_features = loaders["meta"]["num_features"]
    print(f"Num features: {num_features}")
    print("Dropped constant cols:", loaders["meta"]["dropped_constant_cols"])
    print("Early RUL cap:", loaders["meta"]["early_rul"])   


    # Model
    model = LSTMRegressor(LSTMConfig(input_size=num_features, hidden_size=64, num_layers=2, dropout=0.1))

    # Train
    device = "cuda" if torch.cuda.is_available() else "cpu"
    cfg = TrainConfig(
        epochs=30,
        lr=1e-3,
        device=device,
        out_dir="runs",
        run_name="centralized_fd003",
        patience=8,
        monitor="val_rmse",
        mode="min",
        save_best=True,
        seed=42,
    )

    result = train_model(model, loaders["train"], loaders["val"], loaders["test"], cfg)

    # Plot curves (saved to runs/centralized_fd001)
    out_dir = Path(result["paths"]["out_dir"])
    hist = load_history(result["paths"]["history"])

    plot_histories([hist], ["centralized"], key="train_rmse", save_path=out_dir / "train_rmse.png", show=False)
    plot_histories([hist], ["centralized"], key="val_rmse", save_path=out_dir / "val_rmse.png", show=False)
    plot_histories([hist], ["centralized"], key="test_rmse", save_path=out_dir / "test_rmse.png", show=False)

    plot_train_val_test(hist, metric="rmse", save_path=out_dir / "rmse_train_val_test.png", show=False)


    # Evaluate on test (last window per test unit)
    y_true, y_pred = predict(result["model"], loaders["test"], device=device)

    summary = summary_regression(y_true, y_pred, tol_cycles=10.0)
    print("\nTest summary:")
    for k, v in summary.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")

    # Save test plots
    plot_pred_vs_true(y_true, y_pred, save_path=out_dir / "pred_vs_true.png", show=False)
    plot_error_hist(y_true, y_pred, save_path=out_dir / "error_hist.png", show=False)


if __name__ == "__main__":
    main()
