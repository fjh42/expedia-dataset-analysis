
# Expedia Hotel Dataset — Description Report

**Generated:** 2026-04-29 21:48:13  
**Source:** `data/train.csv`

---

## 1. Dataset Overview

| Metric | Value |
| --- | --- |
| Total rows (impressions) | 9,917,530 |
| Total columns | 54 |
| Unique search sessions | 399,344 |
| Unique hotels | 136,886 |
| Unique Expedia sites | 34 |
| Date range | 2012-11-01 00:01:37 → 2013-06-30 23:58:24 |

**Unit of observation:** One hotel impression — a single hotel shown to a user in one search session.
Each row captures whether that hotel was clicked and/or booked.

## 2. Column Schema

Columns grouped by category. See Section 4 for null rates.


### Identifiers & Session

| Column | Type | Description |
| --- | --- | --- |
| `srch_id` | integer | Unique search session ID — groups all hotels shown in one search |
| `date_time` | timestamp | Timestamp of the search event |
| `site_id` | integer | Country-specific Expedia site |
| `visitor_location_country_id` | integer | Country of the searching user |

### Outcome Variables

| Column | Type | Description |
| --- | --- | --- |
| `booking_bool` | binary | **Primary target** — 1 if user booked this hotel (~1–3% positive) |
| `click_bool` | binary | Secondary target — 1 if user clicked this hotel |

### Position & Randomization

| Column | Type | Description |
| --- | --- | --- |
| `position` | integer | Hotel's rank in displayed results (1 = top). **Central confounder.** |
| `random_bool` | binary | 1 if results were randomly sorted for this session (natural experiment) |

### Hotel Quality

| Column | Type | Description |
| --- | --- | --- |
| `prop_id` | integer | Unique hotel identifier |
| `prop_starrating` | integer | Hotel star rating (0–5) |
| `prop_review_score` | float | Aggregate user review score |
| `prop_brand_bool` | binary | 1 if hotel is part of a major brand |
| `prop_location_score1` | float | Expedia's proprietary location attractiveness score |
| `prop_location_score2` | float | Secondary location score — **~21% null, use score1 instead** |
| `prop_log_historical_price` | float | Log of hotel's historical average price |

### Pricing

| Column | Type | Description |
| --- | --- | --- |
| `price_usd` | float | Displayed price for this hotel in this session (right-skewed — use median) |
| `promotion_flag` | binary | 1 if hotel has an active promotion |

### Competitor Pricing (comp1–comp8)

| Column | Type | Description |
| --- | --- | --- |
| `comp{N}_rate` | integer | Expedia vs competitor N: −1 = cheaper, 0 = same, +1 = more expensive |
| `comp{N}_inv` | binary | 1 if competitor N has inventory available |
| `comp{N}_rate_percent_diff` | float | Percentage price difference vs competitor N |

### Search Context

| Column | Type | Description |
| --- | --- | --- |
| `srch_booking_window` | integer | Days between search and check-in |
| `srch_length_of_stay` | integer | Number of nights |
| `srch_adults_count` | integer | Number of adults |
| `srch_children_count` | integer | Number of children |
| `srch_room_count` | integer | Number of rooms requested |
| `srch_saturday_night_bool` | binary | 1 if stay includes a Saturday night |
| `srch_query_affinity_score` | float | How well this hotel matches the user's search query |

### User History

| Column | Type | Description |
| --- | --- | --- |
| `visitor_hist_starrating` | float | User's avg star rating of past bookings — **~94% null** (likely first-time users) |
| `visitor_hist_adr_usd` | float | User's avg daily rate in past bookings — **~94% null** |

### Other

| Column | Type | Description |
| --- | --- | --- |
| `orig_destination_distance` | float | Distance between user location and hotel destination |
| `gross_bookings_usd` | float | Revenue — only populated when booking_bool = 1 |

## 3. Descriptive Statistics — Key Numeric Columns

Stats for columns used in visualizations and models. All stats exclude nulls.

| Column | Min | Median | Mean | Max | Std |
| --- | ---: | ---: | ---: | ---: | ---: |
| `price_usd` | 0.0 | 122.07 | 241.78 | 19,726,328.0 | 14,341.81 |
| `position` | 1 | 16.0 | 16.87 | 40 | 10.43 |
| `prop_starrating` | 0 | 3.0 | 3.18 | 5 | 1.05 |
| `prop_location_score1` | 0.0 | 2.77 | 2.88 | 6.98 | 1.53 |
| `srch_booking_window` | 0 | 17.0 | 37.62 | 498 | 52.11 |
| `srch_length_of_stay` | 1 | 2.0 | 2.39 | 59 | 2.07 |
| `srch_adults_count` | 1 | 2.0 | 1.97 | 9 | 0.86 |
| `srch_room_count` | 1 | 1.0 | 1.11 | 8 | 0.42 |
| `prop_review_score` | 0.0 | 4.0 | 3.78 | 5.0 | 1.05 |

## 4. Missing Values

| Column | Null Count | Null % | Note |
| --- | ---: | ---: | --- |
| `comp1_rate_percent_diff` | 9,732,623 | 98.1% | Competitor data not always available. |
| `comp1_rate` | 9,681,724 | 97.6% | Competitor data not always available. |
| `comp1_inv` | 9,663,097 | 97.4% | Competitor data not always available. |
| `comp4_rate_percent_diff` | 9,653,317 | 97.3% | Competitor data not always available. |
| `gross_bookings_usd` | 9,640,938 | 97.2% | By design: only populated when booking_bool = 1. |
| `comp6_rate` | 9,435,043 | 95.1% | Competitor data not always available. |
| `visitor_hist_starrating` | 9,412,233 | 94.9% | Systematic — likely first-time/infrequent Expedia users. Treat as 'no history'. |
| `visitor_hist_adr_usd` | 9,409,918 | 94.9% | Same population. Do not impute with observed mean. |
| `comp6_inv` | 9,393,385 | 94.7% | Competitor data not always available. |
| `comp4_rate` | 9,297,431 | 93.7% | Competitor data not always available. |
| `comp7_rate` | 9,286,453 | 93.6% | Competitor data not always available. |
| `srch_query_affinity_score` | 9,281,966 | 93.6% | Not always computed by Expedia's pipeline. |
| `comp4_inv` | 9,225,059 | 93.0% | Competitor data not always available. |
| `comp7_inv` | 9,204,355 | 92.8% | Competitor data not always available. |
| `comp3_rate_percent_diff` | 8,973,523 | 90.5% | Competitor data not always available. |
| `comp2_rate_percent_diff` | 8,807,683 | 88.8% | Competitor data not always available. |
| `comp3_rate` | 6,858,257 | 69.2% | Competitor data not always available. |
| `comp3_inv` | 6,625,309 | 66.8% | Competitor data not always available. |
| `comp8_rate` | 6,098,487 | 61.5% | Competitor data not always available. |
| `comp8_inv` | 5,957,142 | 60.1% | Competitor data not always available. |
| `comp2_rate` | 5,876,897 | 59.3% | Competitor data not always available. |
| `comp2_inv` | 5,665,992 | 57.1% | Competitor data not always available. |
| `comp5_rate` | 5,473,236 | 55.2% | Competitor data not always available. |
| `comp5_inv` | 5,196,697 | 52.4% | Competitor data not always available. |
| `orig_destination_distance` | 3,216,461 | 32.4% | User location not always known. |
| `prop_location_score2` | 2,178,380 | 22.0% | High missingness — use prop_location_score1 instead. |
| `prop_review_score` | 14,630 | 0.1% | Minor — safe to impute with median. |

**Key issues:**
- `visitor_hist_*`: ~94% null — systematic, not random. These users have no Expedia booking history.
- `prop_location_score2`: ~21% null — use `prop_location_score1` as the primary location signal.
- `comp{N}_*` columns: partial coverage — consider aggregating into a single competitiveness signal.

## 5. Outcome Variable Analysis


### Overall Rates

| total_bookings | booking_rate_pct | total_clicks | click_rate_pct |
| --- | --- | --- | --- |
| 276,593.00 | 2.79 | 443,672.00 | 4.47 |

### By random_bool (Natural Experiment Split)

| random_bool | impressions | pct_of_data | booking_rate_pct | click_rate_pct |
| --- | --- | --- | --- | --- |
| 0.00 | 6,977,878.00 | 70.40 | 3.74 | 4.40 |
| 1.00 | 2,939,652.00 | 29.60 | 0.54 | 4.66 |

`random_bool=0` → Expedia's algorithm (control). `random_bool=1` → random order (unbiased ground truth for Q2/Q3).

### By Star Rating

| star_rating | impressions | booking_rate_pct | click_rate_pct |
| --- | --- | --- | --- |
| 0.00 | 337,794.00 | 1.65 | 2.90 |
| 1.00 | 34,514.00 | 1.27 | 2.80 |
| 2.00 | 1,788,994.00 | 2.17 | 3.39 |
| 3.00 | 3,897,419.00 | 2.80 | 4.38 |
| 4.00 | 3,045,848.00 | 3.34 | 5.39 |
| 5.00 | 812,961.00 | 2.58 | 4.59 |

### By Position (Top 15 Ranks)

| position | impressions | booking_rate_pct | click_rate_pct |
| --- | --- | --- | --- |
| 1.00 | 398,569.00 | 14.14 | 19.32 |
| 2.00 | 398,466.00 | 9.47 | 13.48 |
| 3.00 | 398,484.00 | 7.17 | 10.55 |
| 4.00 | 386,427.00 | 5.76 | 8.78 |
| 5.00 | 18,600.00 | 1.15 | 2.31 |
| 6.00 | 398,100.00 | 4.50 | 7.10 |
| 7.00 | 389,223.00 | 3.74 | 6.03 |
| 8.00 | 380,362.00 | 3.21 | 5.26 |
| 9.00 | 372,011.00 | 2.73 | 4.65 |
| 10.00 | 346,767.00 | 2.56 | 4.36 |
| 11.00 | 22,327.00 | 0.32 | 0.87 |
| 12.00 | 356,334.00 | 2.15 | 3.73 |
| 13.00 | 349,420.00 | 1.90 | 3.41 |
| 14.00 | 342,018.00 | 1.72 | 3.10 |
| 15.00 | 334,908.00 | 1.60 | 2.93 |

Booking rate drops sharply from position 1 to 2. This is **position bias** — the central methodological issue in this dataset.

### By Brand and Saturday Night

| is_brand_hotel | impressions | booking_rate_pct |
| --- | --- | --- |
| 0.00 | 3,626,799.00 | 2.56 |
| 1.00 | 6,290,731.00 | 2.92 |

| includes_saturday | impressions | booking_rate_pct |
| --- | --- | --- |
| 0.00 | 4,956,223.00 | 2.70 |
| 1.00 | 4,961,307.00 | 2.88 |

## 6. Session-Level Statistics

| total_sessions | avg_hotels_per_session | min_hotels | max_hotels |
| --- | --- | --- | --- |
| 399,344.00 | 24.80 | 5.00 | 38.00 |

| sessions_with_a_booking | pct_sessions_with_booking |
| --- | --- |
| 276,593.00 | 69.26 |

## 7. Limitations and Biases


### Class Imbalance

`booking_bool` is ~1–3% positive — a severely imbalanced classification problem.

- **Risk:** A model predicting 'no booking' for every row gets ~98% accuracy but is useless.
- **Mitigation:** Use AUC-ROC (not accuracy). Use `class_weight='balanced'` in sklearn. Use stratified train/test splits.

### Position Bias

Hotels ranked in position 1 receive far more clicks and bookings than identical hotels in position 8, purely due to display rank.

- `position` is a **confounder**: Expedia's algorithm promotes hotels it expects to convert, so quality and position are correlated.
- **Mitigation 1:** Include `position` as a covariate in regression (statistical control).
- **Mitigation 2:** Restrict analysis to `random_bool=1` sessions where display order was random.
- **Natural experiment:** `random_bool=1` is Expedia's built-in A/B treatment. Booking rates in those sessions reflect genuine user preferences, not algorithmic ranking effects.

### Selection Bias in User History

`visitor_hist_*` columns are ~94% null — not randomly missing. These users have no prior Expedia booking history.
Imputing with the observed mean would misrepresent first-time users. Options: treat null as a 'no history' category, or impute with 0 and add a binary `has_history` flag.

### Price Skew

`price_usd` is right-skewed due to luxury properties. Use **median** (not mean) for summary statistics. Consider log-transforming for regression models.

## 8. Relevant Columns by Research Question


### Q1 — Descriptive: Hotel Attributes and Competitive Pricing vs. Click/Booking Rates

| Role | Columns |
| --- | --- |
| Outcomes | `booking_bool`, `click_bool` |
| Hotel quality | `prop_starrating`, `prop_review_score`, `prop_brand_bool`, `prop_location_score1` |
| Pricing | `price_usd`, `promotion_flag` |
| Competitor pricing | `comp1_rate`–`comp8_rate` |
| Position (confounder) | `position`, `random_bool` |

**Visualizations planned:** booking rate by star rating, by price tier, heatmap (star × price → booking rate), position vs. booking rate, Expedia cheaper vs. more expensive → booking rate.

### Q2 — Logistic Regression: What Predicts Booking Beyond Position?

| Role | Columns |
| --- | --- |
| Target | `booking_bool` |
| Position control | `position` |
| Hotel quality | `prop_starrating`, `prop_review_score`, `prop_brand_bool`, `prop_location_score1` |
| Pricing | `price_usd`, `prop_log_historical_price`, `comp1_rate`, `comp2_rate` |
| Search context | `srch_booking_window`, `srch_length_of_stay`, `srch_adults_count`, `srch_saturday_night_bool` |
| User history | `visitor_hist_starrating`, `visitor_hist_adr_usd` (impute nulls) |
| Unbiased eval subset | `random_bool = 1` rows |

**Collinearity watch list:** `prop_starrating` ↔ `prop_review_score`, `price_usd` ↔ `prop_log_historical_price`, `comp1_rate`–`comp8_rate` (aggregate), `srch_adults_count` ↔ `srch_room_count`.

### Q3 — Ranking Optimization via Random Search

| Role | Columns |
| --- | --- |
| Evaluation data | `random_bool = 1` sessions only |
| Session grouping | `srch_id` |
| Ground truth | `booking_bool` |
| Ranking signals | Predicted booking probability (Q2), `prop_location_score1`, `price_usd` competitiveness |

**Metric:** Mean Reciprocal Rank (MRR). Three-way comparison: random baseline vs. Expedia proxy (sort by `prop_location_score1`) vs. model ranking.