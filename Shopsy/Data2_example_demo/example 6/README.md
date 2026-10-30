# Example 6 — Return risk prediction

**Problem and objective:** Category managers have limited review capacity. Predict return probability at purchase time to prioritize product-page, sizing and quality investigations.

**Business outcome:** Rank purchases for review and estimate how many returns a team reviewing 100 purchases could identify. Predictions do not prove that intervention prevents returns or saves money.

**Inputs:** `inputs/historical_purchases.csv` (12,000 labeled purchases) and `inputs/new_purchases.csv` (500 unlabeled purchases). Four predictors: category, unit price, discount percentage and purchase channel. Target: `returned` (0/1). See `DATA_NOTES.md`.

**Processing:** Validate → train logistic regression and a baseline → independently evaluate → score new purchases and explain priorities.

**Outputs:** A saved model, evaluation report, risk scores and a top-100 review list in `outputs/`.

**Challenges:** Leakage, class imbalance, categorical encoding, threshold trade-offs and confusing synthetic performance with real-world effectiveness.

## Prompt

```text
Build a return-risk prediction example from inputs/, helping category managers prioritize 100 purchases for investigation.
Before creating files, show the architecture, time splits, workflow and outputs for approval.
After approval, create CLAUDE.md with the goal, inputs, outputs and agent roles. Create agents/:
- agent_1_prepare.md: validate DATA_NOTES.md, outcomes and predictors; prepare January–June training, July validation and untouched August test data in working/.
- agent_2_model.md: train logistic regression using category, price, discount and channel, plus a simple baseline. Fit preprocessing on training data only; select settings and threshold on July, then freeze them before testing.
- agent_3_evaluate.md: independently evaluate on August using precision, recall, PR-AUC, a confusion matrix and precision/recall at the top 100. Compare with the baseline; do not tune on test results.
- agent_4_decision.md: use the frozen model to score new purchases; save model artifacts, evaluation.md, risk_scores.csv and top_100_review.csv in outputs/. Explain feature associations and review actions without causal or guaranteed savings claims.
Run 1 → 2 → 3 → 4. Use only the four predictors, never IDs, dates or outcomes as features. Flag weak performance rather than inventing success. New purchases have no known outcomes.
Work locally, preserve inputs, save reproducible work in working/, and disclose unavailable tools or subagent support.
```
