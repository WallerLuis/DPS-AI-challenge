from flask import Flask, request, jsonify
from model import optimize_sarimax, fit_sarimax  
from utils import preprocess_data
import joblib
import os

app = Flask(__name__)


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    year = data.get('year')
    month = data.get('month')
    
    try:
        # Load the trained model
        model_fit = joblib.load('models/sarimax_model.pkl')
        # Forecast
        start_DATUM = f"{year}-{month:02d}-01"
        forecast = model_fit.predict(start=start_DATUM, end=start_DATUM, typ='levels')
        return jsonify({'prediction': int(forecast.iloc[0])})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/retrain", methods=["POST"])
def retrain():
    """
    Endpoint for retraining the model with new data.
    """
    try:
        dataset_path = 'data/monatszahlen2412_verkehrsunfaelle_06_12_24.csv'
        train_data, test_data, full = preprocess_data(dataset_path)
        
        optimize_sarimax(train_data)

        return jsonify({"message": "Model retrained and updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
