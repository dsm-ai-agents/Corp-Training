# Data notes

All records are fictional, generated with seed 20261030. This is a teaching dataset with planted predictive associations and random outcomes, not evidence about Shopsy customers. No model has been trained or evaluated.

## Fields

| Column | Meaning and use |
| --- | --- |
| transaction_id | Unique synthetic purchase ID; join/output identifier, never a predictor |
| purchase_date | ISO purchase date; used only for chronological splitting |
| product_category | Footwear, Apparel, Electronics, Home, Beauty or Grocery; predictor |
| unit_price_inr | Positive pre-discount unit price in INR; predictor |
| discount_pct | Percentage points: 20 means 20%, not 0.20; predictor |
| purchase_channel | Organic, Paid_Search, Social or Email; predictor |
| returned | Historical label: 1 = returned within 30 days; 0 = no return within 30 days |

Each row is one completed single-item purchase eligible for a return. There are no cancelled purchases or repeated customer IDs. The four predictors are captured at purchase time. The new-purchase file deliberately omits the outcome.

## Time and evaluation

Historical purchases cover 1 January–31 August 2026, with full 30-day outcome follow-up available as of 1 October. New purchases are dated 1 October, at prediction time before outcomes are known.

Use January–June for training, July for validation and August for final testing. A label is not supplied for new purchases; their predictive accuracy cannot be measured yet. Use the frozen model for the scoring exercise, without retraining after evaluation.

Encode categorical predictors and scale numeric predictors as appropriate for logistic regression. Learn preprocessing from training data only and handle unseen categories explicitly. Do not oversample before splitting or use identifiers/date as predictors.

Choose any classification threshold on validation data. For the capacity exercise, independently rank the August test purchases and select the top 100; ties use transaction ID. Precision@100 = actual returned purchases in that group / 100. Recall@100 = actual returned purchases in that group / all actual returned purchases in August. The new top-100 file is a prospective review list, not measured successes.

Compare with an always-no-return classifier and a constant training-prevalence probability baseline. Rank ties consistently and explain that the constant baseline has no discrimination. Accuracy alone is insufficient. Report test population size, prevalence, threshold and denominators. Do not use August outcomes to select a model or threshold.

## Interpretation

Return probability was generated from category, price, discount and channel effects with random Bernoulli outcomes. The relationships are deliberately learnable but not deterministic. Some predictors are correlated, so fitted coefficients need not reproduce the generator exactly. No historical inventory, customer history, causal intervention results, cost data or profit labels are supplied.

Risk scores support investigation, not automatic purchase rejection. Category-level summaries can suggest where to review descriptions or sizing, but do not establish a defect or cause. Financial impact requires explicit costs and evidence that an intervention changes outcomes.

`inputs/file_manifest.json` records row counts and checksums. Extract the separate ZIP, open this example folder in Cowork, and paste the README prompt. If subagents are unavailable, disclose that and run the roles sequentially with saved handoffs.
