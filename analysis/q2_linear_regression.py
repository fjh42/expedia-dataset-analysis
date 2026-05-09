"""
Q2 linear regression script (linear probability model).

What this file is for:
- Run a clean, reproducible linear-regression baseline for Q2 on `sample_q2.parquet`.
- Mirror the feature set used in `q2_diagnostics.ipynb` so linear and logistic
  results can be compared directly.
- Output model summary, baseline-vs-model metrics, and top coefficients.

How to use:
1) Ensure dependencies are installed from `requirements.txt`.
2) Run from repository root, e.g.:
   python analysis/q2_linear_regression.py --data data/sample_q2.parquet
3) Read outputs in terminal and use them in milestone write-up.

Notes:
- Target is `booking_bool` (0/1), so this is a linear probability model (LPM).
- LPM is used for interpretability; logistic regression remains the main
  probability-modeling approach.
"""

from __future__ import annotations

import argparse
from typing import Iterable

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


FEATURES: list[str] = [
    "position",
    "prop_starrating",
    "prop_review_score",
    "prop_brand_bool",
    "prop_location_score1",
    "log_price_usd",
    "prop_log_historical_price",
    "srch_booking_window",
    "srch_length_of_stay",
    "srch_adults_count",
    "srch_saturday_night_bool",
]
TARGET = "booking_bool"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Q2 linear regression baseline.")
    parser.add_argument(
        "--data",
        default="data/sample_q2.parquet",
        help="Path to parquet input file.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=100_000,
        help="Max rows used for model fitting; uses all rows if fewer are available.",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Fraction reserved for test split.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible split/sampling.",
    )
    return parser.parse_args()


def regression_metrics(y_true: Iterable[float], y_hat: Iterable[float]) -> dict[str, float]:
    return {
        "RMSE": mean_squared_error(y_true, y_hat, squared=False),
        "MAE": mean_absolute_error(y_true, y_hat),
        "R2": r2_score(y_true, y_hat),
    }


def main() -> None:
    args = parse_args()

    print("\n[1/5] Loading and validating data...")
    df_full = pd.read_parquet(args.data)
    required_cols = FEATURES + [TARGET]
    missing_required = [c for c in required_cols if c not in df_full.columns]
    if missing_required:
        raise ValueError(f"Missing required columns: {missing_required}")

    df_clean = df_full[required_cols].dropna().copy()
    if len(df_clean) > args.sample_size:
        df = df_clean.sample(n=args.sample_size, random_state=args.seed).reset_index(drop=True)
    else:
        df = df_clean.reset_index(drop=True)

    print(f"Full rows        : {len(df_full):,}")
    print(f"Rows after dropna: {len(df_clean):,}")
    print(f"Working sample   : {len(df):,}")
    print(f"Booking rate     : {df[TARGET].mean():.3%}")

    print("\n[2/5] Splitting train/test and building baseline...")
    X = df[FEATURES]
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.seed
    )

    X_train_sm = sm.add_constant(X_train, has_constant="add")
    X_test_sm = sm.add_constant(X_test, has_constant="add")
    y_pred_baseline = np.repeat(y_train.mean(), len(y_test))

    print(f"Train shape      : {X_train.shape}")
    print(f"Test shape       : {X_test.shape}")

    print("\n[3/5] Fitting OLS model...")
    ols_model = sm.OLS(y_train, X_train_sm).fit()
    print(ols_model.summary())

    print("\n[4/5] Evaluating model...")
    y_pred = ols_model.predict(X_test_sm)
    y_pred_clipped = np.clip(y_pred, 0, 1)

    results = pd.DataFrame(
        [
            {"Model": "Baseline (mean)", **regression_metrics(y_test, y_pred_baseline)},
            {"Model": "OLS (raw pred)", **regression_metrics(y_test, y_pred)},
            {"Model": "OLS (clipped 0-1)", **regression_metrics(y_test, y_pred_clipped)},
        ]
    )
    print(results.to_string(index=False))
    outside_bounds = ((y_pred < 0) | (y_pred > 1)).mean()
    print(f"Predictions outside [0,1]: {outside_bounds:.3%}")

    print("\n[5/5] Top coefficient effects...")
    coef_table = (
        pd.DataFrame(
            {
                "feature": ols_model.params.index,
                "coef": ols_model.params.values,
                "pvalue": ols_model.pvalues.values,
            }
        )
        .query("feature != 'const'")
        .assign(abs_coef=lambda d: d["coef"].abs())
    )

    print("\nTop positive effects:")
    print(coef_table.sort_values("coef", ascending=False).head(8).to_string(index=False))

    print("\nTop negative effects:")
    print(coef_table.sort_values("coef", ascending=True).head(8).to_string(index=False))


if __name__ == "__main__":
    main()
