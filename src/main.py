from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error
from utils import preprocess_data, plot
from model import optimize_sarimax, fit_sarimax  
import joblib

# Forecast
def forecast_sarimax(model, test_data):
    forecast = model.get_forecast(steps=len(test_data))
    predicted_mean = forecast.predicted_mean
    return predicted_mean

# Calculate error
def calc_mean_error(test_data, predicted_mean):
    error = mean_absolute_error(test_data, predicted_mean)
    print(f"Mean Absolute Error: {error}")
    return error


def main():
    dataset_path = 'data/monatszahlen2412_verkehrsunfaelle_06_12_24.csv'
    train_data, test_data, full = preprocess_data(dataset_path)

    # print(data_series.head())
    # print(data_series.describe()

    # optimize model sarimax and get best result
    # sarimax_model = optimize_sarimax(train_data)
    
    # already optimized params 
    # sarimax_model = fit_sarimax(train_data)
    
    # Load model
    sarimax_model = joblib.load("models/sarimax_model.pkl")
    forecast = forecast_sarimax(sarimax_model, test_data)

    plot(full, forecast, "sarima")

if __name__ == '__main__':
    main()