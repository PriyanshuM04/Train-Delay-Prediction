import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

# ======== CONFIG ========
ROUTES_FILE = "datasets/processed/master_routes.csv"  
OUTPUT_FILE = "datasets/processed/synthetic_delay_data.csv"

# Create folder if not exists
os.makedirs("datasets/processed", exist_ok=True)

# ======== LOAD ROUTES ========
routes = pd.read_csv(ROUTES_FILE)
train_numbers = routes["TrainNumber"].unique()

# ======== Helper Functions ========
def get_distance_category(distance):
    if distance < 300:
        return random.randint(0, 10)
    elif distance < 800:
        return random.randint(10, 30)
    elif distance < 1500:
        return random.randint(20, 40)
    else:
        return random.randint(30, 60)

def weather_impact(weather):
    if weather == "Clear":
        return 0
    elif weather == "Rain":
        return random.randint(10, 20)
    elif weather == "Fog":
        return random.randint(20, 40)
    elif weather == "Storm":
        return random.randint(40, 90)
    return 0

def festival_impact(impact):
    if impact == "FestivalDay":
        return random.randint(15, 30)
    elif impact == "FestivalEve":
        return random.randint(20, 45)
    return 0

def time_of_day_impact(time_of_day):
    if time_of_day == "Morning":
        return random.randint(-5, 5)
    elif time_of_day == "Day":
        return random.randint(0, 10)
    elif time_of_day == "Evening":
        return random.randint(5, 20)
    elif time_of_day == "Night":
        return random.randint(-10, 5)
    return 0

def get_random_weather():
    return random.choice(["Clear", "Rain", "Fog", "Storm"])

def get_random_festival():
    return random.choice(["None", "FestivalDay", "FestivalEve"])

def get_time_of_day(departure_time):
    if 4 <= departure_time.hour < 9:
        return "Morning"
    elif 9 <= departure_time.hour < 18:
        return "Day"
    elif 18 <= departure_time.hour < 22:
        return "Evening"
    else:
        return "Night"

# ======== Generate synthetic data ========
synthetic_rows = []
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)
num_days = (end_date - start_date).days + 1

for train in train_numbers:
    train_distance = routes[routes["TrainNumber"] == train]["Distance"].max()
    for i in range(num_days):
        current_date = start_date + timedelta(days=i)

        weather = get_random_weather()
        festival = get_random_festival()
        departure_time = datetime.strptime(random.choice(["06:00", "14:00", "20:00", "23:00"]), "%H:%M")
        time_of_day = get_time_of_day(departure_time)

        delay = (
            get_distance_category(train_distance)
            + weather_impact(weather)
            + festival_impact(festival)
            + time_of_day_impact(time_of_day)
        )

        synthetic_rows.append([
            train, current_date.strftime("%Y-%m-%d"), train_distance,
            weather, festival, time_of_day, delay
        ])

# ======== Save to CSV ========
df = pd.DataFrame(synthetic_rows, columns=[
    "TrainNumber", "Date", "Distance", "Weather", "FestivalImpact", "TimeOfDay", "DelayMinutes"
])
df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Synthetic delay data generated and saved to {OUTPUT_FILE}")