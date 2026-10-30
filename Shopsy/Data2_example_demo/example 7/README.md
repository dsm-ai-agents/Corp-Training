# Example 7 — Predict weekly sales

**Business outcome:** Help a category manager plan stock for upcoming weeks using the planned price, discount and advertising budget. Better unit estimates can support fewer stockouts and less excess stock; this exercise does not measure actual savings.

**Problem and objective:** Predict weekly units sold for one fictional product using simple multiple linear regression with three inputs.

**Inputs:** `historical_weekly_sales.csv` has 104 weeks and just four columns: unit price, discount percentage, planned ad spend and units sold. `planned_weeks.csv` has four upcoming weeks with only the three inputs. See `DATA_NOTES.md` for dates and splits.

**Processing:** Validate and split by time → train regression and a baseline → evaluate on unseen weeks → predict upcoming sales and explain planning implications.

**Outputs:** Saved model, `weekly_predictions.csv`, `evaluation.md` and `actual_vs_predicted.png` in `outputs/`.

**Challenges:** Small samples, noisy demand, time leakage, extrapolation and confusing a sales prediction with a replenishment order.

## Prompt

```text
Predict weekly units sold to help a category manager plan stock from inputs/.
Before creating files, show the business objective, workflow, time splits and outputs for approval.
After approval, create CLAUDE.md with the goal, folders, inputs, outputs and agent roles. Create agents/:
- agent_1_prepare.md: validate DATA_NOTES.md and the four-column historical file; preserve chronological order and split data rows 1–72 for training, 73–88 for validation and 89–104 for testing.
- agent_2_regression.md: train multiple linear regression using unit_price_inr, discount_pct and planned_ad_spend_inr to predict weekly_units_sold. Compare with the training-mean baseline. Fit preprocessing only on training data, use validation for decisions, and freeze before testing.
- agent_3_evaluate_plan.md: evaluate once on test weeks with MAE, RMSE and R-squared; create actual_vs_predicted.png, then score the four planned weeks. Save model artifacts, weekly_predictions.csv and evaluation.md in outputs/, explaining uncertainty and inventory implications.
Run 1 → 2 → 3. Use only the three predictors, never row numbers or dates. Keep the model frozen for scoring; do not tune on test results. Report weak performance honestly and flag negative or out-of-range predictions.
Keep work local, preserve inputs, and save reproducible steps in working/. Treat predictions as planning estimates, not guaranteed sales, causal effects or order quantities. Disclose unavailable tools or subagent support.
```
