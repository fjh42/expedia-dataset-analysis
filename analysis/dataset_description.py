"""
dataset_description.py
ORIE 3120 — Expedia Hotel Dataset
Generates a Markdown dataset description for PM1 write-up.

Usage:
    python analysis/dataset_description.py
    python analysis/dataset_description.py --path data/train.csv --out analysis/dataset_description.md
"""

import duckdb
import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--path", default="data/train.csv")
parser.add_argument("--out",  default="analysis/dataset_description.md")
args = parser.parse_args()

CSV = args.path
OUT = args.out

con = duckdb.connect()
lines = []


def h1(t): lines.append(f"\n# {t}\n")
def h2(t): lines.append(f"\n## {t}\n")
def h3(t): lines.append(f"\n### {t}\n")
def p(t=""): lines.append(str(t))


def run(sql):
    return con.execute(sql).df()


def md_table(df):
    cols = list(df.columns)
    rows = [
        "| " + " | ".join(
            f"{v:,.2f}" if isinstance(v, float) else f"{v:,}" if isinstance(v, int) else str(v)
            for v in row
        ) + " |"
        for _, row in df.iterrows()
    ]
    return "\n".join(
        ["| " + " | ".join(cols) + " |",
         "| " + " | ".join("---" for _ in cols) + " |"]
        + rows
    )


# ── Header ───────────────────────────────────────────────────────────────────────
h1("Expedia Hotel Dataset — Description Report")
p(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
p(f"**Source:** `{CSV}`\n")
p("---")

# ── 1. Overview ───────────────────────────────────────────────────────────────────
print("→ Section 1: Overview")
h2("1. Dataset Overview")

nrows = con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{CSV}', nullstr='NULL')").fetchone()[0]

overview = run(f"""
    SELECT
        COUNT(DISTINCT srch_id)                     AS unique_sessions,
        COUNT(DISTINCT prop_id)                     AS unique_hotels,
        COUNT(DISTINCT site_id)                     AS unique_sites,
        MIN(date_time)::VARCHAR                     AS earliest_search,
        MAX(date_time)::VARCHAR                     AS latest_search
    FROM read_csv_auto('{CSV}', nullstr='NULL')
""")
r = overview.iloc[0]

p(f"| Metric | Value |")
p(f"| --- | --- |")
p(f"| Total rows (impressions) | {nrows:,} |")
p(f"| Total columns | 54 |")
p(f"| Unique search sessions | {int(r.unique_sessions):,} |")
p(f"| Unique hotels | {int(r.unique_hotels):,} |")
p(f"| Unique Expedia sites | {int(r.unique_sites):,} |")
p(f"| Date range | {r.earliest_search} → {r.latest_search} |")

p()
p("**Unit of observation:** One hotel impression — a single hotel shown to a user in one search session.")
p("Each row captures whether that hotel was clicked and/or booked.")

# ── 2. Column Schema ──────────────────────────────────────────────────────────────
print("→ Section 2: Column schema")
h2("2. Column Schema")
p("Columns grouped by category. See Section 4 for null rates.\n")

SCHEMA = {
    "Identifiers & Session": [
        ("`srch_id`",                       "integer",  "Unique search session ID — groups all hotels shown in one search"),
        ("`date_time`",                     "timestamp","Timestamp of the search event"),
        ("`site_id`",                       "integer",  "Country-specific Expedia site"),
        ("`visitor_location_country_id`",   "integer",  "Country of the searching user"),
    ],
    "Outcome Variables": [
        ("`booking_bool`",  "binary", "**Primary target** — 1 if user booked this hotel (~1–3% positive)"),
        ("`click_bool`",    "binary", "Secondary target — 1 if user clicked this hotel"),
    ],
    "Position & Randomization": [
        ("`position`",      "integer", "Hotel's rank in displayed results (1 = top). **Central confounder.**"),
        ("`random_bool`",   "binary",  "1 if results were randomly sorted for this session (natural experiment)"),
    ],
    "Hotel Quality": [
        ("`prop_id`",                   "integer", "Unique hotel identifier"),
        ("`prop_starrating`",           "integer", "Hotel star rating (0–5)"),
        ("`prop_review_score`",         "float",   "Aggregate user review score"),
        ("`prop_brand_bool`",           "binary",  "1 if hotel is part of a major brand"),
        ("`prop_location_score1`",      "float",   "Expedia's proprietary location attractiveness score"),
        ("`prop_location_score2`",      "float",   "Secondary location score — **~21% null, use score1 instead**"),
        ("`prop_log_historical_price`", "float",   "Log of hotel's historical average price"),
    ],
    "Pricing": [
        ("`price_usd`",        "float",  "Displayed price for this hotel in this session (right-skewed — use median)"),
        ("`promotion_flag`",   "binary", "1 if hotel has an active promotion"),
    ],
    "Competitor Pricing (comp1–comp8)": [
        ("`comp{N}_rate`",              "integer", "Expedia vs competitor N: −1 = cheaper, 0 = same, +1 = more expensive"),
        ("`comp{N}_inv`",               "binary",  "1 if competitor N has inventory available"),
        ("`comp{N}_rate_percent_diff`", "float",   "Percentage price difference vs competitor N"),
    ],
    "Search Context": [
        ("`srch_booking_window`",       "integer", "Days between search and check-in"),
        ("`srch_length_of_stay`",       "integer", "Number of nights"),
        ("`srch_adults_count`",         "integer", "Number of adults"),
        ("`srch_children_count`",       "integer", "Number of children"),
        ("`srch_room_count`",           "integer", "Number of rooms requested"),
        ("`srch_saturday_night_bool`",  "binary",  "1 if stay includes a Saturday night"),
        ("`srch_query_affinity_score`", "float",   "How well this hotel matches the user's search query"),
    ],
    "User History": [
        ("`visitor_hist_starrating`", "float", "User's avg star rating of past bookings — **~94% null** (likely first-time users)"),
        ("`visitor_hist_adr_usd`",    "float", "User's avg daily rate in past bookings — **~94% null**"),
    ],
    "Other": [
        ("`orig_destination_distance`", "float", "Distance between user location and hotel destination"),
        ("`gross_bookings_usd`",        "float", "Revenue — only populated when booking_bool = 1"),
    ],
}

for group, cols in SCHEMA.items():
    h3(group)
    p("| Column | Type | Description |")
    p("| --- | --- | --- |")
    for col, dtype, desc in cols:
        p(f"| {col} | {dtype} | {desc} |")

# ── 3. Descriptive Stats ──────────────────────────────────────────────────────────
print("→ Section 3: Descriptive stats")
h2("3. Descriptive Statistics — Key Numeric Columns")
p("Stats for columns used in visualizations and models. All stats exclude nulls.\n")

STAT_COLS = [
    "price_usd",
    "position",
    "prop_starrating",
    "prop_location_score1",
    "srch_booking_window",
    "srch_length_of_stay",
    "srch_adults_count",
    "srch_room_count",
]

p("| Column | Min | Median | Mean | Max | Std |")
p("| --- | ---: | ---: | ---: | ---: | ---: |")

for col in STAT_COLS:
    print(f"  stats: {col}")
    r = con.execute(f"""
        SELECT
            ROUND(MIN("{col}"), 2)       AS min,
            ROUND(MEDIAN("{col}"), 2)    AS median,
            ROUND(AVG("{col}"), 2)       AS mean,
            ROUND(MAX("{col}"), 2)       AS max,
            ROUND(STDDEV("{col}"), 2)    AS std
        FROM read_csv_auto('{CSV}', nullstr='NULL')
        WHERE "{col}" IS NOT NULL
    """).fetchone()
    p(f"| `{col}` | {r[0]:,} | {r[1]:,} | {r[2]:,} | {r[3]:,} | {r[4]:,} |")

# prop_review_score needs explicit cast since DuckDB may type it as VARCHAR
print("  stats: prop_review_score")
try:
    r = con.execute(f"""
        SELECT
            ROUND(MIN(TRY_CAST(prop_review_score AS DOUBLE)), 2),
            ROUND(MEDIAN(TRY_CAST(prop_review_score AS DOUBLE)), 2),
            ROUND(AVG(TRY_CAST(prop_review_score AS DOUBLE)), 2),
            ROUND(MAX(TRY_CAST(prop_review_score AS DOUBLE)), 2),
            ROUND(STDDEV(TRY_CAST(prop_review_score AS DOUBLE)), 2)
        FROM read_csv_auto('{CSV}', nullstr='NULL')
        WHERE TRY_CAST(prop_review_score AS DOUBLE) IS NOT NULL
    """).fetchone()
    p(f"| `prop_review_score` | {r[0]:,} | {r[1]:,} | {r[2]:,} | {r[3]:,} | {r[4]:,} |")
except Exception as e:
    p(f"| `prop_review_score` | — | — | — | — | — |")

# ── 4. Missing Values ─────────────────────────────────────────────────────────────
print("→ Section 4: Missing values")
h2("4. Missing Values")

# Query only the columns we know have meaningful nulls
NULL_COLS = [
    "visitor_hist_starrating", "visitor_hist_adr_usd",
    "prop_location_score2", "prop_review_score",
    "orig_destination_distance", "srch_query_affinity_score",
    "gross_bookings_usd",
    "comp1_rate", "comp2_rate", "comp3_rate", "comp4_rate",
    "comp5_rate", "comp6_rate", "comp7_rate", "comp8_rate",
    "comp1_inv", "comp2_inv", "comp3_inv", "comp4_inv",
    "comp5_inv", "comp6_inv", "comp7_inv", "comp8_inv",
    "comp1_rate_percent_diff", "comp2_rate_percent_diff",
    "comp3_rate_percent_diff", "comp4_rate_percent_diff",
]

null_parts = [
    f"SUM(CASE WHEN \"{c}\" IS NULL THEN 1 ELSE 0 END) AS \"{c}\""
    for c in NULL_COLS
]
null_row = con.execute(f"SELECT {', '.join(null_parts)} FROM read_csv_auto('{CSV}', nullstr='NULL')").fetchone()

NULL_NOTES = {
    "visitor_hist_starrating":      "Systematic — likely first-time/infrequent Expedia users. Treat as 'no history'.",
    "visitor_hist_adr_usd":         "Same population. Do not impute with observed mean.",
    "prop_location_score2":         "High missingness — use prop_location_score1 instead.",
    "prop_review_score":            "Minor — safe to impute with median.",
    "orig_destination_distance":    "User location not always known.",
    "srch_query_affinity_score":    "Not always computed by Expedia's pipeline.",
    "gross_bookings_usd":           "By design: only populated when booking_bool = 1.",
}
for i in range(1, 9):
    for s in ["rate", "inv", "rate_percent_diff"]:
        NULL_NOTES[f"comp{i}_{s}"] = "Competitor data not always available."

p("| Column | Null Count | Null % | Note |")
p("| --- | ---: | ---: | --- |")
null_data = list(zip(NULL_COLS, null_row))
null_data.sort(key=lambda x: -x[1])
for col, nc in null_data:
    if nc == 0:
        continue
    pct = nc / nrows * 100
    note = NULL_NOTES.get(col, "")
    p(f"| `{col}` | {nc:,} | {pct:.1f}% | {note} |")

p()
p("**Key issues:**")
p("- `visitor_hist_*`: ~94% null — systematic, not random. These users have no Expedia booking history.")
p("- `prop_location_score2`: ~21% null — use `prop_location_score1` as the primary location signal.")
p("- `comp{N}_*` columns: partial coverage — consider aggregating into a single competitiveness signal.")

# ── 5. Outcome Analysis ───────────────────────────────────────────────────────────
print("→ Section 5: Outcome analysis")
h2("5. Outcome Variable Analysis")

h3("Overall Rates")
ov = run(f"""
    SELECT
        SUM(booking_bool)                    AS total_bookings,
        ROUND(AVG(booking_bool)*100, 3)      AS booking_rate_pct,
        SUM(click_bool)                      AS total_clicks,
        ROUND(AVG(click_bool)*100, 3)        AS click_rate_pct
    FROM read_csv_auto('{CSV}', nullstr='NULL')
""")
p(md_table(ov))

h3("By random_bool (Natural Experiment Split)")
rb = run(f"""
    SELECT
        random_bool,
        COUNT(*)                              AS impressions,
        ROUND(COUNT(*)*100.0/{nrows}, 1)      AS pct_of_data,
        ROUND(AVG(booking_bool)*100, 3)       AS booking_rate_pct,
        ROUND(AVG(click_bool)*100, 3)         AS click_rate_pct
    FROM read_csv_auto('{CSV}', nullstr='NULL')
    GROUP BY random_bool
    ORDER BY random_bool
""")
p(md_table(rb))
p()
p("`random_bool=0` → Expedia's algorithm (control). `random_bool=1` → random order (unbiased ground truth for Q2/Q3).")

h3("By Star Rating")
sr = run(f"""
    SELECT prop_starrating AS star_rating,
           COUNT(*)                          AS impressions,
           ROUND(AVG(booking_bool)*100, 3)   AS booking_rate_pct,
           ROUND(AVG(click_bool)*100, 3)     AS click_rate_pct
    FROM read_csv_auto('{CSV}', nullstr='NULL')
    GROUP BY prop_starrating
    ORDER BY prop_starrating
""")
p(md_table(sr))

h3("By Position (Top 15 Ranks)")
pos = run(f"""
    SELECT position,
           COUNT(*)                          AS impressions,
           ROUND(AVG(booking_bool)*100, 3)   AS booking_rate_pct,
           ROUND(AVG(click_bool)*100, 3)     AS click_rate_pct
    FROM read_csv_auto('{CSV}', nullstr='NULL')
    WHERE position <= 15
    GROUP BY position
    ORDER BY position
""")
p(md_table(pos))
p()
p("Booking rate drops sharply from position 1 to 2. This is **position bias** — the central methodological issue in this dataset.")

h3("By Brand and Saturday Night")
brand = run(f"""
    SELECT prop_brand_bool AS is_brand_hotel,
           COUNT(*)                          AS impressions,
           ROUND(AVG(booking_bool)*100, 3)   AS booking_rate_pct
    FROM read_csv_auto('{CSV}', nullstr='NULL')
    GROUP BY prop_brand_bool ORDER BY prop_brand_bool
""")
p(md_table(brand))
p()
sat = run(f"""
    SELECT srch_saturday_night_bool AS includes_saturday,
           COUNT(*)                          AS impressions,
           ROUND(AVG(booking_bool)*100, 3)   AS booking_rate_pct
    FROM read_csv_auto('{CSV}', nullstr='NULL')
    GROUP BY srch_saturday_night_bool ORDER BY srch_saturday_night_bool
""")
p(md_table(sat))

# ── 6. Session Stats ──────────────────────────────────────────────────────────────
print("→ Section 6: Session stats")
h2("6. Session-Level Statistics")

sess = run(f"""
    SELECT
        COUNT(DISTINCT srch_id)               AS total_sessions,
        ROUND(AVG(n), 1)                      AS avg_hotels_per_session,
        MIN(n)                                AS min_hotels,
        MAX(n)                                AS max_hotels
    FROM (SELECT srch_id, COUNT(*) AS n FROM read_csv_auto('{CSV}', nullstr='NULL') GROUP BY srch_id)
""")
p(md_table(sess))
p()
sess2 = run(f"""
    SELECT
        SUM(booked)                           AS sessions_with_a_booking,
        ROUND(AVG(booked)*100, 2)             AS pct_sessions_with_booking
    FROM (SELECT srch_id, MAX(booking_bool) AS booked FROM read_csv_auto('{CSV}', nullstr='NULL') GROUP BY srch_id)
""")
p(md_table(sess2))

# ── 7. Limitations & Biases ───────────────────────────────────────────────────────
print("→ Section 7: Limitations and biases")
h2("7. Limitations and Biases")

h3("Class Imbalance")
p("`booking_bool` is ~1–3% positive — a severely imbalanced classification problem.\n")
p("- **Risk:** A model predicting 'no booking' for every row gets ~98% accuracy but is useless.")
p("- **Mitigation:** Use AUC-ROC (not accuracy). Use `class_weight='balanced'` in sklearn. Use stratified train/test splits.")

h3("Position Bias")
p("Hotels ranked in position 1 receive far more clicks and bookings than identical hotels in position 8, purely due to display rank.\n")
p("- `position` is a **confounder**: Expedia's algorithm promotes hotels it expects to convert, so quality and position are correlated.")
p("- **Mitigation 1:** Include `position` as a covariate in regression (statistical control).")
p("- **Mitigation 2:** Restrict analysis to `random_bool=1` sessions where display order was random.")
p("- **Natural experiment:** `random_bool=1` is Expedia's built-in A/B treatment. Booking rates in those sessions reflect genuine user preferences, not algorithmic ranking effects.")

h3("Selection Bias in User History")
p("`visitor_hist_*` columns are ~94% null — not randomly missing. These users have no prior Expedia booking history.")
p("Imputing with the observed mean would misrepresent first-time users. Options: treat null as a 'no history' category, or impute with 0 and add a binary `has_history` flag.")

h3("Price Skew")
p("`price_usd` is right-skewed due to luxury properties. Use **median** (not mean) for summary statistics. Consider log-transforming for regression models.")

# ── 8. Columns by Research Question ──────────────────────────────────────────────
print("→ Section 8: Columns by research question")
h2("8. Relevant Columns by Research Question")

h3("Q1 — Descriptive: Hotel Attributes and Competitive Pricing vs. Click/Booking Rates")
p("| Role | Columns |")
p("| --- | --- |")
p("| Outcomes | `booking_bool`, `click_bool` |")
p("| Hotel quality | `prop_starrating`, `prop_review_score`, `prop_brand_bool`, `prop_location_score1` |")
p("| Pricing | `price_usd`, `promotion_flag` |")
p("| Competitor pricing | `comp1_rate`–`comp8_rate` |")
p("| Position (confounder) | `position`, `random_bool` |")
p()
p("**Visualizations planned:** booking rate by star rating, by price tier, heatmap (star × price → booking rate), position vs. booking rate, Expedia cheaper vs. more expensive → booking rate.")

h3("Q2 — Logistic Regression: What Predicts Booking Beyond Position?")
p("| Role | Columns |")
p("| --- | --- |")
p("| Target | `booking_bool` |")
p("| Position control | `position` |")
p("| Hotel quality | `prop_starrating`, `prop_review_score`, `prop_brand_bool`, `prop_location_score1` |")
p("| Pricing | `price_usd`, `prop_log_historical_price`, `comp1_rate`, `comp2_rate` |")
p("| Search context | `srch_booking_window`, `srch_length_of_stay`, `srch_adults_count`, `srch_saturday_night_bool` |")
p("| User history | `visitor_hist_starrating`, `visitor_hist_adr_usd` (impute nulls) |")
p("| Unbiased eval subset | `random_bool = 1` rows |")
p()
p("**Collinearity watch list:** `prop_starrating` ↔ `prop_review_score`, `price_usd` ↔ `prop_log_historical_price`, `comp1_rate`–`comp8_rate` (aggregate), `srch_adults_count` ↔ `srch_room_count`.")

h3("Q3 — Ranking Optimization via Random Search")
p("| Role | Columns |")
p("| --- | --- |")
p("| Evaluation data | `random_bool = 1` sessions only |")
p("| Session grouping | `srch_id` |")
p("| Ground truth | `booking_bool` |")
p("| Ranking signals | Predicted booking probability (Q2), `prop_location_score1`, `price_usd` competitiveness |")
p()
p("**Metric:** Mean Reciprocal Rank (MRR). Three-way comparison: random baseline vs. Expedia proxy (sort by `prop_location_score1`) vs. model ranking.")

# ── Write output ──────────────────────────────────────────────────────────────────
output = "\n".join(lines)
print(output)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(output)

print(f"\n✓ Saved to {OUT}")
