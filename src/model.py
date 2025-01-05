import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error
import itertools

def preprocess_data(file_path):
    data = pd.read_csv(file_path, delimiter=",")

    data.columns = [
            'KATEGORIE', 'GRUND', 'JAHR', 'MONAT', 'WERT', 
            'VORJAHRESWERT', 'VERAEND_VORMONAT_PROZENT', 
            'VERAEND_VORJAHRESMONAT_PROZENT', 'ZWOELF_MONATE_MITTELWERT'
        ]

    # Filter for relevant data
    filtered_data = data[
        (data['KATEGORIE'] == 'Alkoholunfälle') &
        (data['GRUND'] == 'insgesamt') &
        # (data['JAHR'] <= 2021) &
        # (data['JAHR'] >= 2018) &
        (data['MONAT'] != "Summe")
    ]

    # print(filtered_data.head(30))
    # Drop unnecessary columns 
    filtered_data = filtered_data[['KATEGORIE', 'GRUND','JAHR', 'MONAT', 'WERT']].dropna()

    
    # WERT to numeric data
    filtered_data['WERT'] = pd.to_numeric(filtered_data['WERT'], errors='coerce')

    # Create Column DATUM for datetime
    filtered_data['DATUM'] = pd.to_datetime(filtered_data['MONAT'], format='%Y%m', errors='coerce')

    # fixing monat
    filtered_data['MONAT'] = filtered_data['MONAT'].astype(str).str[-2:]

    filtered_data.dropna(subset=['WERT', 'DATUM'])

    # print(filtered_data.head(30))

    # sort data correctly (graph fix)
    filtered_data = filtered_data.sort_values(by=['DATUM'], ascending=True)
    #print(filtered_data.head())

    # Set index to 'DATUM'
    filtered_data.set_index('DATUM', inplace=True)
    #print(filtered_data.head(20))

    # Set manual Monthly start frequency, if not warning error
    filtered_data = filtered_data.asfreq('MS') 
    
    return filtered_data['WERT']

def fit_sarimax(data_series):
    # Split into training and testing
    train_data = data_series.loc[data_series.index < '2021-01-01']
    test_data = data_series.loc[data_series.index >= '2021-01-01']

    # Fit SARIMA model
    model = SARIMAX(train_data, order=(2, 1, 2), seasonal_order=(0, 2, 2, 12))
    results = model.fit()

    # Forecast
    forecast = results.get_forecast(steps=len(test_data))
    predicted_mean = forecast.predicted_mean

    # Calculate error
    error = mean_absolute_error(test_data, predicted_mean)
    print(f"Mean Absolute Error: {error}")

    return results, predicted_mean

def train_sarimax(data_series):

    # Split into training and testing
    train_data = data_series.loc[data_series.index < '2021-01-01']
    test_data = data_series.loc[data_series.index >= '2021-01-01']
    
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
    results = model.fit(disp=False)

    # Forecast
    forecast = results.get_forecast(steps=len(test_data))
    predicted_mean = forecast.predicted_mean

    # Calculate error
    error = mean_absolute_error(test_data, predicted_mean)
    print(f"Mean Absolute Error: {error}")

    return results, predicted_mean

def plot(data, forecast, modelname):
    plt.figure(figsize=(10, 6))
    plt.plot(data, label='historische Daten')
    if not forecast.empty:
        plt.plot(forecast, label='Forecast', linestyle='--')
    plt.legend()
    plt.title('Alkoholunfälle in Bayern')
    plt.xlabel('Jahr')
    plt.ylabel('Anzahl an Unfälle')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    # plt.show()
    plt.savefig(modelname + ".png")
    plt.close()


if __name__ == '__main__':
    dataset_path = 'data/monatszahlen2412_verkehrsunfaelle_06_12_24.csv'
    data_series = preprocess_data(dataset_path)

    # print(data_series.head())
    # print(data_series.describe()

    # from statsmodels.tsa.seasonal import seasonal_decompose
    # seasonal_decompose(data_series, model='additive', period=12).plot()
    # plt.show()

    # train sarimax
    sarimax_model, future_forecast = train_sarimax(data_series)
    
    plot(data_series, future_forecast, "sarima")
    
    sarimax_model, future_forecast = fit_sarimax(data_series)
    # print(future_forecast.describe())
