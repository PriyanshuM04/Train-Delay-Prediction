# Testing for single train

import requests
import pandas as pd

API_KEY = "0416b07540babf9356cbe96262fd6c81"
TRAIN_NO = "12305"

url = f"https://indianrailapi.com/api/v2/TrainSchedule/apikey/{API_KEY}/TrainNumber/{TRAIN_NO}"

response = requests.get(url)
data = response.json()

if data["ResponseCode"] == "200" and 'Route' in data:
    print(f"✅ Successfully fetched route for Train No. {TRAIN_NO}\n")

    route = data['Route']
    df = pd.DataFrame(route)[['StationName', 'StationCode', 'ArrivalTime', 'DepartureTime', 'Distance']]
    print(df)

    filename = f"./Trial/{TRAIN_NO}_route_schedule.csv"
    df.to_csv(filename, index=False)
    print(f"\n✅ Schedule saved as '{filename}'")

else:
    print("❌ Error: Could not fetch data.")
    print("📝 Message:", data.get("Message", "No message provided."))
