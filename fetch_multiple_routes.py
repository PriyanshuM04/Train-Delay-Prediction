import requests
import pandas as pd
import os

API_KEY = "0416b07540babf9356cbe96262fd6c81"
train_numbers = ['12305', '12801', '12306', '12002', '12951', '12245', '12953', '12860', '12301', '12903']

output_folder = "Routes"
os.makedirs(output_folder, exist_ok=True)

for train_no in train_numbers:
    url = f"https://indianrailapi.com/api/v2/TrainSchedule/apikey/{API_KEY}/TrainNumber/{train_no}"
    response = requests.get(url)
    data = response.json()

    if data.get("ResponseCode") == "200" and "Route" in data:
        route = data["Route"]
        df = pd.DataFrame(route)[["StationName", "StationCode", "ArrivalTime", "DepartureTime", "Distance"]]
        df["TrainNumber"] = train_no

        file_name = os.path.join(output_folder, f"{train_no}_route.csv")
        df.to_csv(file_name, index = False)
        print(f"✅ Saved: {file_name}")

    else:
        print(f"❌ Failed to fetch data for train {train_no}. Reason: {data.get("Message", "Unknown error")}")

