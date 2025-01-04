import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
        (data['JAHR'] <= 2020) &
        # (data['JAHR'] >= 2018) &
        (data['MONAT'] != "Summe")
    ]

    # Drop unnecessary columns 
    filtered_data = filtered_data[['KATEGORIE', 'GRUND','JAHR', 'MONAT', 'WERT']].dropna()

    
    # WERT to numeric data
    filtered_data['WERT'] = pd.to_numeric(filtered_data['WERT'], errors='coerce')

    # Create Column DATUM for datetime
    filtered_data['DATUM'] = pd.to_datetime(filtered_data['MONAT'], format='%Y%m', errors='coerce')

    # fixing monat
    filtered_data['MONAT'] = filtered_data['MONAT'].astype(str).str[-2:]

    filtered_data.dropna(subset=['WERT', 'DATUM'])

    # sort data correctly (graph fix)
    filtered_data = filtered_data.sort_values(by=['DATUM'], ascending=False)
    #print(filtered_data.head())

    # Set index to 'DATUM'
    filtered_data.set_index('DATUM', inplace=True)
    #print(filtered_data.head(20))
    
    return filtered_data['WERT']

def plot_forecast(data):
    plt.figure(figsize=(10, 6))
    plt.plot(data, label='historische Daten')

    plt.legend()
    plt.title('Alkoholunfälle in Bayern')
    plt.xlabel('Jahr')
    plt.ylabel('Anzahl an Unfälle')
    plt.show()


if __name__ == '__main__':
    dataset_path = 'data/monatszahlen2412_verkehrsunfaelle_06_12_24.csv'
    data_series = preprocess_data(dataset_path)

    print(data_series.head())
    # print(data_series.describe())

    # data_series = data_series.dropna().asfreq('D')  # Drop NaNs and set frequency

    # print(data_series.head())
    
    plot_forecast(data_series)
