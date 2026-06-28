"""
Feature Tools — Technical indicators and transformations.
"""
from __future__ import annotations

from typing import Dict
import numpy as np
import pandas as pd

from ..base import BaseFeatureTool
from ..registry import ToolRegistry


class RSITool(BaseFeatureTool):
    """Relative Strength Index."""

    def _compute_impl(self, data: Dict[str, pd.DataFrame]) -> np.ndarray:
        window = self.params.get("window", 14)
        features = []

        for ticker, df in data.get("stock", {}).items():
            if "close" not in df.columns:
                features.append([0.0] * window)
                continue

            close = df["close"].values
            if len(close) < window + 1:
                features.append([0.0] * window)
                continue

            delta = np.diff(close)
            gain = np.where(delta > 0, delta, 0.0)
            loss = np.where(delta < 0, -delta, 0.0)

            avg_gain = np.mean(gain[-window:])
            avg_loss = np.mean(loss[-window:])

            if avg_loss == 0:
                rsi = 100.0
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))

            # Normalize to [0, 1] and add recent RSI trajectory
            rsi_norm = rsi / 100.0
            recent_rsi = np.array([rsi_norm] * min(window, len(close)))
            if len(recent_rsi) < window:
                recent_rsi = np.pad(recent_rsi, (window - len(recent_rsi), 0), constant_values=0.5)

            features.append(recent_rsi[-window:])

        return np.array(features) if features else np.array([])


class MACDTool(BaseFeatureTool):
    """Moving Average Convergence Divergence."""

    def _compute_impl(self, data: Dict[str, pd.DataFrame]) -> np.ndarray:
        fast = self.params.get("fast", 12)
        slow = self.params.get("slow", 26)
        signal = self.params.get("signal", 9)

        features = []
        for ticker, df in data.get("stock", {}).items():
            if "close" not in df.columns or len(df) < slow + signal:
                features.append([0.0] * 3)
                continue

            close = df["close"].values
            ema_fast = pd.Series(close).ewm(span=fast, adjust=False).mean().values
            ema_slow = pd.Series(close).ewm(span=slow, adjust=False).mean().values
            macd = ema_fast - ema_slow
            macd_signal = pd.Series(macd).ewm(span=signal, adjust=False).mean().values
            histogram = macd - macd_signal

            # Normalize by price
            price = close[-1]
            features.append([
                macd[-1] / price if price != 0 else 0.0,
                macd_signal[-1] / price if price != 0 else 0.0,
                histogram[-1] / price if price != 0 else 0.0,
            ])

        return np.array(features) if features else np.array([])


class ZScoreTool(BaseFeatureTool):
    """Cross-sectional z-score normalization."""

    def _compute_impl(self, data: Dict[str, pd.DataFrame]) -> np.ndarray:
        window = self.params.get("window", 20)

        # Collect returns across all assets
        all_returns = {}
        for group_name, group_data in data.items():
            for ticker, df in group_data.items():
                if "close" in df.columns and len(df) > window:
                    returns = df["close"].pct_change().dropna().values
                    all_returns[ticker] = returns[-window:]

        if not all_returns:
            return np.array([])

        # Compute cross-sectional mean/std per time step
        tickers = list(all_returns.keys())
        n = len(tickers)
        max_len = max(len(r) for r in all_returns.values())

        # Pad shorter series
        returns_matrix = np.zeros((n, max_len))
        for i, ticker in enumerate(tickers):
            r = all_returns[ticker]
            returns_matrix[i, -len(r):] = r

        # Cross-sectional z-score (per time step)
        cs_mean = returns_matrix.mean(axis=0)
        cs_std = returns_matrix.std(axis=0) + 1e-8
        z_scores = (returns_matrix - cs_mean) / cs_std

        # Return last time step z-scores per asset
        return z_scores[:, -1].reshape(-1, 1)


class PCATOOL(BaseFeatureTool):
    """PCA on feature matrix for dimensionality reduction."""

    def _compute_impl(self, data: Dict[str, pd.DataFrame]) -> np.ndarray:
        k = self.params.get("k", 5)

        # Build feature matrix from all numeric data
        all_features = []
        tickers = []

        for group_name, group_data in data.items():
            for ticker, df in group_data.items():
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) == 0:
                    continue
                feat = df[numeric_cols].iloc[-1].values
                if len(feat) > 0:
                    all_features.append(feat)
                    tickers.append(ticker)

        if len(all_features) < 2:
            return np.array([])

        X = np.array(all_features)
        # Standardize
        X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)

        # PCA via SVD
        U, S, Vt = np.linalg.svd(X, full_matrices=False)
        k = min(k, Vt.shape[0])
        components = Vt[:k]

        # Project
        X_pca = X @ components.T

        return X_pca  # [n_assets, k]


class WaveletTool(BaseFeatureTool):
    """Wavelet decomposition for multi-resolution features."""

    def _compute_impl(self, data: Dict[str, pd.DataFrame]) -> np.ndarray:
        level = self.params.get("level", 3)

        try:
            import pywt
        except ImportError:
            # Fallback: simple rolling statistics at different windows
            return self._fallback_impl(data)

        features = []
        for ticker, df in data.get("stock", {}).items():
            if "close" not in df.columns or len(df) < 2 ** level:
                features.append([0.0] * (level * 2))
                continue

            close = df["close"].values
            # Wavelet decomposition
            coeffs = pywt.wavedec(close, 'db4', level=level)

            # Extract statistics from each level
            feat = []
            for c in coeffs:
                feat.extend([np.mean(c), np.std(c)])

            features.append(feat)

        return np.array(features) if features else np.array([])

    def _fallback_impl(self, data: Dict[str, pd.DataFrame]) -> np.ndarray:
        """Rolling mean/std at multiple windows as wavelet proxy."""
        windows = [5, 10, 20, 40]
        features = []

        for ticker, df in data.get("stock", {}).items():
            if "close" not in df.columns:
                features.append([0.0] * (len(windows) * 2))
                continue

            close = df["close"].values
            feat = []
            for w in windows:
                if len(close) >= w:
                    feat.append(np.mean(close[-w:]) / close[-1] - 1.0)
                    feat.append(np.std(close[-w:]) / close[-1])
                else:
                    feat.extend([0.0, 0.0])
            features.append(feat)

        return np.array(features) if features else np.array([])


class CrossSectionalTool(BaseFeatureTool):
    """Cross-sectional ranking and momentum."""

    def _compute_impl(self, data: Dict[str, pd.DataFrame]) -> np.ndarray:
        # Compute returns for all assets
        returns = {}
        for group_name, group_data in data.items():
            for ticker, df in group_data.items():
                if "close" in df.columns and len(df) > 1:
                    ret = df["close"].pct_change().iloc[-1]
                    if not np.isnan(ret):
                        returns[ticker] = ret

        if len(returns) < 2:
            return np.array([])

        tickers = list(returns.keys())
        rets = np.array([returns[t] for t in tickers])

        # Cross-sectional rank (percentile)
        ranks = np.argsort(np.argsort(rets)) / (len(rets) - 1)

        # Momentum: 20-day return rank
        mom_returns = {}
        for group_name, group_data in data.items():
            for ticker, df in group_data.items():
                if "close" in df.columns and len(df) > 20:
                    ret_20 = df["close"].pct_change(20).iloc[-1]
                    if not np.isnan(ret_20):
                        mom_returns[ticker] = ret_20

        mom_ranks = np.zeros_like(ranks)
        if mom_returns:
            mom_tickers = list(mom_returns.keys())
            mom_rets = np.array([mom_returns[t] for t in mom_tickers])
            mom_ranks_vals = np.argsort(np.argsort(mom_rets)) / (len(mom_rets) - 1)
            for i, t in enumerate(tickers):
                if t in mom_returns:
                    idx = mom_tickers.index(t)
                    mom_ranks[i] = mom_ranks_vals[idx]

        return np.column_stack([ranks, mom_ranks])


# Register all feature tools
ToolRegistry.register_feature("rsi", RSITool)
ToolRegistry.register_feature("macd", MACDTool)
ToolRegistry.register_feature("zscore", ZScoreTool)
ToolRegistry.register_feature("pca", PCATOOL)
ToolRegistry.register_feature("wavelet", WaveletTool)
ToolRegistry.register_feature("cross_sectional", CrossSectionalTool)