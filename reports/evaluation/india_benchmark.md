# CarbonScope 2.0 - ML Forecasting Evaluation Report: India

- **Validation Strategy:** Chronological Holdout Split
- **Training Period:** 1975 – 2015 (41 Years)
- **Testing Period:** 2016 – 2025 (10 Out-of-Sample Years)
- **Best Performing Model:** **`Linear Regression`** (Test RMSE: `202.24 Mt CO2eq`)

## Model Benchmark Summary

| Model Architecture        |   Train MAE (Mt) |   Train RMSE (Mt) |   Train R² |   Test MAE (Mt) |   Test MSE (Mt²) |   Test RMSE (Mt) |   Test MAPE (%) |   Test R² | Is_Best   |
|:--------------------------|-----------------:|------------------:|-----------:|----------------:|-----------------:|-----------------:|----------------:|----------:|:----------|
| Linear Regression         |            19.62 |             26.81 |     0.9986 |          166.47 |  40899.8         |           202.24 |            4.32 |    0.7691 | True      |
| Gradient Boosting         |             3.59 |              4.39 |     1      |          689.86 | 611991           |           782.3  |           17.08 |   -2.4555 | False     |
| Random Forest             |            15.07 |             24.77 |     0.9988 |          782.3  | 777279           |           881.63 |           19.41 |   -3.3888 | False     |
| Support Vector Regression |           156.25 |            298.89 |     0.8295 |         1966.62 |      4.11627e+06 |          2028.86 |           50.22 |  -22.2419 | False     |

> [!NOTE]
> Models were evaluated strictly on out-of-sample future years (2016-2025). High training scores are displayed alongside testing scores to verify absence of overfitting.
