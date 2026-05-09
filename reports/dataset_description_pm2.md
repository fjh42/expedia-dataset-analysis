# Dataset Description

## Source and Collection

The dataset used in this project consists of real hotel search and booking logs from Expedia, originally released as part of the 2013 ICDM/Expedia Personalized Hotel Search competition hosted on Kaggle. The data was collected through server-side event logging on Expedia's platform: every time a user submitted a hotel search, the platform recorded the full ordered list of properties displayed to that user, along with any subsequent clicks or bookings. Because the data originates directly from Expedia's production system, it reflects authentic user behavior rather than survey responses or synthetic generation — each value in the dataset corresponds to a real event that occurred on the platform during the collection window.

The dataset spans eight months of activity, from November 1, 2012 through June 30, 2013. This single time window is an important constraint on generalizability: seasonal patterns specific to winter and spring travel (such as holiday bookings and spring break trips) are captured, but summer peak-season behavior is not. Results and model coefficients should therefore be interpreted as characteristic of this period rather than as universal constants of hotel search behavior. The dataset contains 34 distinct Expedia site IDs, each corresponding to a country-specific version of the platform (e.g., Expedia.com, Expedia.co.uk), and 136,886 unique hotel properties spanning a broad range of destinations.

## Unit of Observation

Each row in the dataset represents a single hotel impression: one property shown to one user during one search session. The total dataset contains **9,917,530 impressions** across **399,344 unique search sessions**, with a median of approximately 25 hotels displayed per search (range: 5–38). Search sessions are identified by `srch_id`, which groups all the hotels a user saw in a single query. The combination of `srch_id` and `prop_id` (the unique hotel identifier) uniquely identifies each row. The outcome for each impression is recorded at the row level via two binary variables: `click_bool` (whether the user clicked on this hotel) and `booking_bool` (whether the user ultimately booked it).

## Key Columns

The 54 columns fall into six conceptual groups:

**Outcome variables.** `booking_bool` is the primary target (1 if booked, 0 otherwise; overall rate: 2.79%). `click_bool` is a secondary target capturing whether the user clicked into the hotel's detail page (overall rate: 4.47%).

**Position and randomization.** `position` records the rank at which this hotel appeared in the displayed results (1 = topmost). `random_bool` is a binary flag set to 1 for sessions in which Expedia deliberately shuffled the result order at random rather than applying its ranking algorithm (29.6% of all sessions). This flag defines a natural experiment embedded in the data and is central to the methodological approach described in the Research Questions section.

**Hotel quality.** `prop_starrating` (0–5 stars), `prop_review_score` (0–5 aggregate user rating), `prop_brand_bool` (major brand affiliation), and `prop_location_score1` (Expedia's proprietary location attractiveness score, range 0–7) together characterize the supply-side quality of each property.

**Pricing.** `price_usd` is the displayed price for this hotel in this session. The distribution is highly right-skewed — the median is \$122 while the mean is \$242 and the maximum exceeds \$19 million due to luxury and data-entry outliers — so median statistics are used throughout. `prop_log_historical_price` captures the log of the hotel's long-run average price, providing a stable baseline independent of session-specific promotions. `promotion_flag` indicates an active promotional discount.

**Competitor pricing.** Eight sets of columns (`comp1_*` through `comp8_*`) record whether Expedia's price for this property is lower (−1), equal (0), or higher (+1) than each of eight unnamed competitor platforms, whether those competitors have the property in inventory, and the percentage price difference. These columns have very high missingness (55–98% null across different competitors), reflecting that competitor price scraping is incomplete and inconsistent.

**Search context.** `srch_booking_window` (days between search and check-in date), `srch_length_of_stay` (nights), `srch_adults_count`, `srch_children_count`, `srch_room_count`, `srch_saturday_night_bool`, and `srch_query_affinity_score` (how well this property matches the user's query text) describe the demand-side characteristics of each search.

**User history.** `visitor_hist_starrating` and `visitor_hist_adr_usd` record the average star rating and average daily rate of this user's prior Expedia bookings. These columns are approximately 94% null — not randomly, but because the vast majority of users in the dataset have no prior Expedia booking history. Imputing these nulls with the observed mean would misrepresent first-time users; instead, nulls are treated as a "no history" category by imputing with 0 and adding a binary `has_history` indicator.

## The Built-In Natural Experiment

A notable structural feature of the dataset is the `random_bool` flag. In approximately 30% of sessions, Expedia randomly permuted the order of hotels shown to the user. These sessions serve as an unbiased ground truth: because display order was random, any variation in click and booking rates across hotels within these sessions reflects genuine user preferences rather than the effect of rank position. Booking rates in `random_bool=1` sessions (0.54%) are far lower than in algorithmically ranked sessions (3.74%), which quantifies how much of the observed booking activity in normal sessions is attributable to Expedia's algorithm placing higher-quality or better-priced hotels at the top. This split is used throughout the analysis to disentangle real feature effects from position-driven artifacts.

## Limitations and Biases

**Position bias.** The most important limitation of this dataset is that display position is a powerful confounder. Hotels shown in position 1 have a booking rate of 14.1%, compared to 3.2% at position 8 and 1.6% at position 15 — a nearly 9× difference between top and bottom. Because Expedia's algorithm likely places hotels it expects to perform well at the top, position and hotel quality are correlated. Any naive analysis that regresses booking probability on hotel attributes without accounting for position will conflate the effect of position with the effect of the attributes themselves. This is addressed either by including `position` as a covariate in regression models or by restricting analysis to `random_bool=1` sessions.

**Class imbalance.** `booking_bool` is positive in only 2.79% of rows. A model that predicts "not booked" for every impression would achieve 97.2% accuracy while providing no useful information. Accuracy is therefore not a valid performance metric; area under the ROC curve (AUC-ROC) is used instead. Models are trained with `class_weight='balanced'` to prevent the majority class from dominating the loss function, and train/test splits are stratified on `booking_bool` to preserve the class ratio in both partitions.

**Missing competitor data.** The competitor pricing columns (`comp1_*` through `comp8_*`) are nearly entirely missing for most competitor–property combinations, with null rates ranging from 55% to 98%. This likely reflects the practical difficulty of scraping prices from competing platforms in real time; a null value does not mean the competitor has no price, only that the price was not captured. These columns are therefore aggregated into summary indicators rather than used individually.

**Temporal and geographic scope.** The data covers a single eight-month window from one major online travel agency. Platform-specific effects (Expedia's particular user base, its ranking algorithm as of 2012–2013, its market share in each country) may not generalize to other booking platforms or to contemporary behavior. The dataset does not identify which specific destinations or countries the hotels are located in — only the user's origin country and the Expedia site used — limiting geographic analysis.

**Observational data.** With the exception of the `random_bool` natural experiment, this is observational data. Causal claims about the effect of hotel attributes on booking probability require careful control for confounders (primarily `position`) and carry the standard limitations of observational inference, including the possibility of unobserved confounders such as brand recognition or destination desirability that are not captured in the dataset's columns.
