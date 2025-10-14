from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import os

from data_fetching.fetch_external_data import get_weather, get_festival_impact

# --- Load model once ---
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "delay_predictor.pkl")
ROUTE_PATH = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed", "master_routes.csv")

model = joblib.load(MODEL_PATH)
routes_df = pd.read_csv(ROUTE_PATH)

app = FastAPI(title="Indian Railway Delay Predictor API")

# --- Request body model ---
class PredictionRequest(BaseModel):
    train_number: str
    date: str  # YYYY-MM-DD

@app.get("/debug/routes")
def debug_routes():
    return {
        "total_rows": len(routes_df),
        "sample": routes_df.head(5).to_dict(orient="records")
    }



@app.post("/predict")
def predict_delay(req: PredictionRequest):
    train_number = req.train_number
    date = req.date

    # --- Get train details ---
    train_data = routes_df[routes_df["TrainNumber"] == train_number]
    if train_data.empty:
        return {"error": f"Train number {train_number} not found in routes data"}

    distance = train_data["Distance"].max()
    city_name = train_data["StationName"].iloc[0]

    # --- Fetch external data ---
    weather = get_weather(city_name, pd.to_datetime(date).date())
    festival = get_festival_impact(pd.to_datetime(date).date()) or "None"

    # --- Time of day from departure time ---
    departure_time = pd.to_datetime(train_data["DepartureTime"].iloc[0], format="%H:%M")
    hour = departure_time.hour
    if 4 <= hour < 9:
        time_of_day = "Morning"
    elif 9 <= hour < 18:
        time_of_day = "Day"
    elif 18 <= hour < 22:
        time_of_day = "Evening"
    else:
        time_of_day = "Night"

    # --- Prepare input ---
    input_df = pd.DataFrame([{
        "Distance": distance,
        "Weather": weather,
        "FestivalImpact": festival,
        "TimeOfDay": time_of_day
    }])

    input_df = pd.get_dummies(input_df)
    for col in model.feature_names_in_:
        if col not in input_df.columns:
            input_df[col] = 0
    input_df = input_df[model.feature_names_in_]

    # --- Predict ---
    predicted_delay = float(model.predict(input_df)[0])

    return {
        "train_number": train_number,
        "date": date,
        "predicted_delay_minutes": round(predicted_delay, 2),
        "weather": weather,
        "festival": festival,
        "time_of_day": time_of_day
    }

