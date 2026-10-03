# model_lstm.py
from __future__ import annotations

from dataclasses import dataclass
import torch
import torch.nn as nn


@dataclass(frozen=True)
class LSTMConfig:
    input_size: int
    hidden_size: int = 64
    num_layers: int = 2
    dropout: float = 0.1  # applied between LSTM layers if num_layers>1
    bidirectional: bool = False


class LSTMRegressor(nn.Module):
    """
    Simple LSTM regressor for RUL prediction.

    Expects input X: [batch, seq_len, input_size]
    Outputs: [batch] (scalar per sample)
    """
    def __init__(self, cfg: LSTMConfig):
        super().__init__()
        self.cfg = cfg
        self.lstm = nn.LSTM(
            input_size=cfg.input_size,
            hidden_size=cfg.hidden_size,
            num_layers=cfg.num_layers,
            dropout=(cfg.dropout if cfg.num_layers > 1 else 0.0),
            batch_first=True,
            bidirectional=cfg.bidirectional,
        )
        out_dim = cfg.hidden_size * (2 if cfg.bidirectional else 1)
        self.head = nn.Sequential(
            nn.Linear(out_dim, out_dim),
            nn.ReLU(),
            nn.Linear(out_dim, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, T, F]
        out, _ = self.lstm(x)          # out: [B, T, H]
        last = out[:, -1, :]           # [B, H]
        y = self.head(last).squeeze(-1)  # [B]
        return y
