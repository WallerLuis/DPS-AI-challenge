import pandas as pd
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
        # (data['JAHR'] <= 2021) &
        # (data['JAHR'] >= 2015) &
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

    # Set manual Monthly start frequency, if not -> warning error
    filtered_data = filtered_data.asfreq('MS')

    # shrink to only
    filtered_data = filtered_data['WERT']

    # split into train and test data
    train_data = filtered_data.loc[filtered_data.index < '2020-01-01'] 
    test_data = filtered_data.loc[filtered_data.index >= '2020-01-01']
    
    return train_data, test_data, filtered_data

# Plotting the data + Forecast based on modelname
def plot(data, forecast, modelname):
    plt.figure(figsize=(12, 6))
    plt.plot(data, label='historische Daten', linestyle='-', color='b', linewidth= 0.7)
    if not forecast.empty:
        plt.plot(forecast, label='Vorhersage', linestyle='--', color='r')
    plt.legend()
    plt.title('Alkoholunfälle in Bayern')
    plt.xlabel('Jahr')
    plt.ylabel('Anzahl an Unfälle')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    # plt.show()
    plt.savefig("pic/" + modelname + ".png")
    plt.close()