import pandas as pd
import numpy as np
import os
import random

# === Load the merged routes dataset ===
routes_path = "MergedData/master_routes.csv"  # path to your merged dataset
df = pd.read_csv(routes_path)

# === Add extra columns for conditions ===
# For simplicity, randomly assigning weather and festival flags
weather_conditions = ["Clear", "Rain", "Fog", "Storm"]
df["Weather"] = np.random.choice(weather_conditions, size=len(df))
df["FestivalImpact"] = np.random.choice(["None", "FestivalDay", "NearFestival"], size=len(df))
df["DepartureHour"] = pd.to_datetime(df["DepartureTime"], errors='coerce').dt.hour.fillna(10)

# === Helper functions ===
def base_delay(distance):
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

def festival_impact(festival):
    if festival == "FestivalDay":
        return random.randint(15, 30)
    elif festival == "NearFestival":
        return random.randint(20, 45)
    return 0

def time_of_day_impact(hour):
    if 4 <= hour < 9:   # Morning
        return random.randint(-5, 5)
    elif 9 <= hour < 18: # Day
        return random.randint(0, 10)
    elif 18 <= hour < 22: # Evening Peak
        return random.randint(5, 20)
    else: # Night
        return random.randint(-10, 5)

def train_type_adjustment(train_type):
    if "Rajdhani" in str(train_type) or "Shatabdi" in str(train_type) or "Premium" in str(train_type):
        return 0.75  # 25% less delay
    elif "Passenger" in str(train_type):
        return 1.20  # 20% more delay
    return 1.0

# === Calculate synthetic delay ===
synthetic_delays = []
for idx, row in df.iterrows():
    dist = row.get("Distance", 500)   # fallback
    weather = row["Weather"]
    festival = row["FestivalImpact"]
    hour = row["DepartureHour"]
    train_type = row.get("TrainType", "Express")

    delay = (base_delay(dist) +
             weather_impact(weather) +
             festival_impact(festival) +
             time_of_day_impact(hour) +
             random.randint(-5, 5)) * train_type_adjustment(train_type)
    
    synthetic_delays.append(round(max(delay, 0), 2))

df["SyntheticDelay(min)"] = synthetic_delays

# === Save to CSV ===
output_path = "FinalDatasets/synthetic_train_delays.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df.to_csv(output_path, index=False)
print(f"✅ Synthetic delay dataset created: {output_path}")
