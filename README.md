# Expedia Hotel Search & Booking Analysis

Course project for **ORIE 3120 (Spring 2026)** using the [Kaggle Expedia hotel dataset](https://www.kaggle.com/datasets/vijeetnigam26/expedia-hotel?select=train.csv).

We study what drives hotel **clicks** and **bookings**, with a focus on:
- hotel features (star rating, reviews, price, brand, location score),
- search context,
- and **position bias** using `random_bool` sessions (randomized ranking).

## Project questions

- **Q1:** Which hotel and pricing factors are associated with higher click/booking rates?
- **Q2:** After controlling for display position, which factors still predict booking?
- **Q3:** How can we use randomized sessions for cleaner ranking analysis?

## Repository guide

- `analysis/dataset_description.py` — generates `analysis/dataset_description.md` from `data/train.csv`.
- `analysis/prepare_samples.py` — creates:
  - `data/sample_q2.parquet` (10% sample of full data),
  - `data/sample_q3.parquet` (50% of `random_bool=1` sessions).
- `analysis/q2_diagnostics.ipynb` — logistic-regression diagnostic notebook for Q2 (`booking_bool`), including assumption checks and interpretation support for the report.
- `analysis/q2_linear_regression.ipynb` — linear probability model notebook for Q2 (baseline + OLS + diagnostics) aligned to the logistic notebook feature set.
- `analysis/q2_linear_regression.py` — script version of the Q2 linear model workflow for reproducible terminal runs and teammate handoff.
- `reports/` — milestone write-up text and report outlines.
- `vizualizations/` — exported charts used in reports.
- `requirements.txt` — Python dependencies.

## Data setup

1. Download `train.csv` from Kaggle.
2. Put it in `data/train.csv`.

`data/*.csv` is ignored in git, but parquet samples are included for quick analysis.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Use a fresh virtual environment for this project to avoid binary-compatibility
issues between global/anaconda packages and pinned `numpy`/`pandas` versions.

Dependency smoke test:

```bash
python -c "import numpy, pandas, statsmodels, sklearn; print('ok')"
```

If you see a numpy/pandas binary mismatch error, recreate the venv and reinstall:

```bash
rm -rf .venv
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Generate dataset description:

```bash
python analysis/dataset_description.py --path data/train.csv --out analysis/dataset_description.md
```

Build sample parquet files (run from `analysis/`):

```bash
cd analysis
python prepare_samples.py --path ../data/train.csv
cd ..
```

Run Q2 diagnostics by opening `analysis/q2_diagnostics.ipynb`.

Run Q2 linear notebook:

```bash
jupyter notebook analysis/q2_linear_regression.ipynb
```

Run Q2 linear script from repository root:

```bash
python analysis/q2_linear_regression.py --data data/sample_q2.parquet
```

## Q2 modeling workflow

1. Create `sample_q2.parquet` with `analysis/prepare_samples.py`.
2. Run `analysis/q2_diagnostics.ipynb` to validate logistic-model assumptions and interpret feature behavior.
3. Run `analysis/q2_linear_regression.ipynb` or `analysis/q2_linear_regression.py` for a linear probability benchmark.
4. Compare coefficient direction/significance and metric behavior across logistic vs linear outputs.
5. Use both analyses in milestone writing: logistic for primary inference, linear for transparent comparison and robustness context.

## Expected Q2 outputs

After running the Q2 notebooks/script, report these deliverables:

- Model quality metrics from linear analysis: RMSE, MAE, and R2 (plus baseline comparison).
- Coefficient interpretation: top positive and top negative feature effects, including direction and magnitude.
- Diagnostics summary: residual behavior for linear model and assumption-check takeaways from logistic diagnostics.
- Cross-model consistency check: where linear and logistic results agree or differ in feature direction/significance.
- Milestone-ready conclusion bullets: what appears robust, what is likely confounded by position/ranking, and key caveats.

## Attribution

Dataset source: Expedia ICDM 2013 competition data redistributed on Kaggle.  
This repository contains course project materials.
