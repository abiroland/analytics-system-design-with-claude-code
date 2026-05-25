# Forecast Engine

Fits ARIMA or Prophet models on a time series, evaluates on a held-out period, and returns forecasts with prediction intervals.

## Trigger

Fires when an agent needs forward-looking projections — price forecasts, volume trajectories, or growth market identification.

## Instructions

When asked to forecast a time series:

1. **Train-test split:**
   ```python
   split_idx = int(len(series) * train_ratio)  # default train_ratio=0.8
   train = series[:split_idx]
   test = series[split_idx:]
   ```
   For time series, always split chronologically — never shuffle.

2. **ARIMA (default):**
   ```python
   from statsmodels.tsa.arima.model import ARIMA
   from pmdarima import auto_arima

   # Auto-select order via AIC
   auto_model = auto_arima(
       train, seasonal=True, m=52,
       stepwise=True, suppress_warnings=True,
       error_action="ignore",
   )
   order = auto_model.order
   seasonal_order = auto_model.seasonal_order

   model = ARIMA(train, order=order, seasonal_order=seasonal_order)
   fitted = model.fit()
   forecast = fitted.get_forecast(steps=forecast_horizon)
   ```

3. **Prophet (when requested):**
   ```python
   from prophet import Prophet

   prophet_df = pd.DataFrame({"ds": dates, "y": values})
   model = Prophet(yearly_seasonality=True, weekly_seasonality=False)
   model.fit(prophet_df_train)
   future = model.make_future_dataframe(periods=forecast_horizon, freq="W")
   forecast = model.predict(future)
   ```

4. **Default parameters:**
   - `forecast_horizon`: 26 weeks (6 months ahead)
   - `train_ratio`: 0.8
   - `model_type`: "arima"

5. **Prediction intervals:** Report both 80% and 95% intervals. For ARIMA use `get_forecast(alpha=0.20)` and `get_forecast(alpha=0.05)`. For Prophet these come from `yhat_lower`/`yhat_upper`.

6. **Accuracy metrics on test set:**
   - RMSE: `sqrt(mean((actual - predicted)^2))`
   - MAE: `mean(|actual - predicted|)`
   - MAPE: `mean(|actual - predicted| / |actual|) * 100`
   Report all three. Flag if MAPE > 20% (poor forecast quality).

7. **Model artifacts:** Save fitted model to `outputs/models/forecast_{target}_{region}_{type}.pkl` using joblib:
   ```python
   import joblib
   joblib.dump(fitted, path)
   ```

8. **Group forecasting:** When forecasting across multiple regions/types, fit separate models per group. Do not pool across groups — each (region, type) pair gets its own model.

9. **Filter to city-level regions** by default. State which regions were forecast in the output.

10. **Always cite** the target column, data file, date range, and model parameters in any report.
