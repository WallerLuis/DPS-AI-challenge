from statsmodels.tsa.statespace.sarimax import SARIMAX
import itertools
import joblib


# hyperparameter optimization via grid search for sarimax(p, d, q, P, D, Q, s)
def optimize_sarimax(train_data):    

    # Define parameter ranges
    p = d = q = range(0, 3)  # Non-seasonal parameters
    P = D = Q = range(0, 3)  # Seasonal parameters
    s = [12]  # Seasonality (e.g., monthly data)

    pdq = list(itertools.product(p, d, q))
    seasonal_pdq = list(itertools.product(P, D, Q, s))

    best_aic = float("inf")
    best_params = None
    best_seasonal_params = None

    for param in pdq:
        for seasonal_param in seasonal_pdq:
            print(f"Order: {param}, seasonal: {seasonal_param}")
            try:
                model = SARIMAX(
                    train_data,
                    order=param,
                    seasonal_order=seasonal_param,
                    enforce_stationarity=False,
                    enforce_invertibility=False
                )
                results = model.fit(disp=False)
                
                print(results.aic)
                if results.aic < best_aic:
                    best_aic = results.aic
                    best_params = param
                    best_seasonal_params = seasonal_param
            except Exception as e:
                # Handle exceptions for invalid parameter combinations
                continue

    print(f'Best ARIMA parameters: {best_params}')
    print(f'Best seasonal parameters: {best_seasonal_params} with AIC: {best_aic}')

    # Fit the best SARIMA model
    model = SARIMAX(
        train_data,
        order=best_params,
        seasonal_order=best_seasonal_params,
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    model = model.fit(disp=False)

    # save SARIMAX model 
    joblib.dump(model, "models/sarimax_model.pkl")
    return model

def fit_sarimax(train_data):

    # Fit SARIMA model
    model = SARIMAX(
        train_data,
        order=(2, 1, 2),
        seasonal_order=(0, 2, 2, 12),
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    model = model.fit(disp=False)

    # save SARIMAX model 
    joblib.dump(model, "models/sarimax_model.pkl")

    return model  