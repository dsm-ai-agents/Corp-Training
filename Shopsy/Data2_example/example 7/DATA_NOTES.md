# Data notes

Fictional weekly sales for one product in one market, with seed 2026103007. The business predicts units, not currency revenue. No model has been run.

| Historical column | Meaning |
| --- | --- |
| unit_price_inr | Planned pre-discount price per unit, INR |
| discount_pct | Planned percentage points; 10 means 10% |
| planned_ad_spend_inr | Advertising budget known before the week starts, INR; not realized end-of-week spend |
| weekly_units_sold | Observed synthetic unit sales for the completed week; prediction target |

There are exactly four historical columns: three predictors plus the outcome. The planned file has the same three predictors and no outcomes. This is multiple linear regression because it uses three inputs.

## Calendar and evaluation

Rows are in chronological order. Historical data row 1 is the week starting 28 October 2024; each subsequent row advances seven days. Row 104 starts 19 October 2026. The synthetic planning cutoff is 25 October 2026. Planned rows 1–4 start 26 October, 2 November, 9 November and 16 November 2026 respectively. Dates are recorded in the manifest to keep the modeling CSV at four columns. Preserve row order and attach dates to output predictions.

Train on rows 1–72, validate on rows 73–88, and test on rows 89–104. Row numbers exclude the header. Avoid random shuffling. Fit preprocessing using training data only. Freeze all modeling decisions after validation, then evaluate on the final 16 weeks without tuning or refitting. Use that same model for the four future predictions.

Baseline: predict the mean weekly units from the training period for every validation/test week. MAE measures average absolute error in units; RMSE penalizes larger errors; R-squared compares against test-period mean variation and can be negative. Compare regression and baseline on the same test weeks. Do not imply a few test weeks establish reliable production performance.

Save week_start, predicted_units and any warning flags in weekly_predictions.csv. Keep raw predictions for evaluation; if presenting whole units for planning, show rounding separately. The planned weeks are unlabelled, so their accuracy cannot yet be measured. Explain prediction uncertainty; label any error-based range as a heuristic unless a justified prediction interval is calculated.

## Synthetic assumptions and business use

The generator plants lower demand at higher prices and higher demand with larger discounts and ad budgets, plus random noise. This makes the exercise learnable without making outcomes deterministic. These associations are invented for teaching; coefficients do not establish causal effects or real price elasticity.

The example assumes adequate availability and no changing product mix, major seasonality or structural trend. Real sales forecasting needs those issues checked. Planned inputs lie within training ranges. Do not extrapolate confidently beyond the observed ranges.

A sales estimate is only one input to replenishment. Current stock, inbound deliveries, lead times, service levels and costs are absent. Discuss stock planning implications without fabricating recommended purchase orders or savings.

The manifest records counts and checksums. Extract the ZIP, open this folder in Cowork and paste the README prompt. If subagents are unavailable, disclose that and execute the roles sequentially with saved handoffs.
