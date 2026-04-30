"""
prepare_samples.py
ORIE 3120 — Expedia Hotel Dataset
Extracts working parquet samples from the full CSV (run once).

Q2 sample: 10% bernoulli of full dataset → data/sample_q2.parquet
Q3 sample: 50% of random_bool=1 sessions (all hotels kept) → data/sample_q3.parquet

Usage:
    python analysis/prepare_samples.py
    python analysis/prepare_samples.py --path data/train.csv
"""

import duckdb
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--path", default="data/train.csv")
args = parser.parse_args()

CSV = args.path
con = duckdb.connect()

# ── Q2: 10% bernoulli sample of full dataset ──────────────────────────────────
print("Extracting Q2 sample (10% of full dataset)...")
con.execute(f"""
    COPY (
        SELECT * FROM read_csv_auto('{CSV}', nullstr='NULL')
        USING SAMPLE 10 PERCENT (bernoulli, 42)
    ) TO 'data/sample_q2.parquet' (FORMAT parquet)
""")
q2_stats = con.execute("SELECT COUNT(*), ROUND(AVG(booking_bool)*100,3) FROM 'data/sample_q2.parquet'").fetchone()
print(f"  Q2: {q2_stats[0]:,} rows | booking rate: {q2_stats[1]}%")

# ── Q3: 50% of random_bool=1 sessions, all hotels within each ────────────────
print("Extracting Q3 sample (50% of random_bool=1 sessions)...")
con.execute(f"""
    COPY (
        SELECT t.*
        FROM read_csv_auto('{CSV}', nullstr='NULL') t
        INNER JOIN (
            SELECT srch_id
            FROM (
                SELECT DISTINCT srch_id
                FROM read_csv_auto('{CSV}', nullstr='NULL')
                WHERE random_bool = 1
            )
            USING SAMPLE 50 PERCENT (bernoulli, 42)
        ) s ON t.srch_id = s.srch_id
    ) TO 'data/sample_q3.parquet' (FORMAT parquet)
""")
q3_stats = con.execute("SELECT COUNT(*), COUNT(DISTINCT srch_id) FROM 'data/sample_q3.parquet'").fetchone()
print(f"  Q3: {q3_stats[0]:,} rows | {q3_stats[1]:,} sessions")

print("\nDone.")
print("  data/sample_q2.parquet — use for logistic regression (Q2)")
print("  data/sample_q3.parquet — use for ranking optimization (Q3)")
print()
print("Load in scripts with:")
print("  import duckdb; con = duckdb.connect()")
print("  df = con.execute(\"SELECT * FROM 'data/sample_q2.parquet'\").df()")
