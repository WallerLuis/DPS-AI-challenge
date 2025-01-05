import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error

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
    data_series = data_series.asfreq('MS') 
    
    return filtered_data['WERT']

def fit_sarimax(data_series):
    # Split into training and testing
    train_data = data_series.loc[data_series.index < '2021-01-01']
    test_data = data_series.loc[data_series.index >= '2021-01-01']

    # Fit SARIMA model
    model = SARIMAX(train_data, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
    results = model.fit()

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

    print(data_series.head())
    # print(data_series.describe()

    # from statsmodels.tsa.seasonal import seasonal_decompose
    # seasonal_decompose(data_series, model='additive', period=12).plot()
    # plt.show()

    
    # train sarimax
    sarimax_model, future_forecast = fit_sarimax(data_series)
    # print(future_forecast.describe())
    plot(data_series, future_forecast, "sarima")
