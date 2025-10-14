import streamlit as st
import pandas as pd
import joblib
import os
from data_fetching.fetch_external_data import get_weather, get_festival_impact

st.set_page_config(page_title="Train Delay Predictor", layout="centered")
st.title("🚆 Indian Railway Delay Predictor")

# Load model and columns
MODEL_PATH = os.path.join("models", "delay_predictor.pkl")
DATA_PATH = os.path.join("datasets", "processed", "master_routes.csv")
model = joblib.load(MODEL_PATH)
routes = pd.read_csv(DATA_PATH)
train_numbers = routes["TrainNumber"].unique()

# Sidebar
st.sidebar.header("Prediction Inputs")
train_no = st.sidebar.selectbox("Select Train Number", train_numbers)
date = st.sidebar.date_input("Select Date")

if st.sidebar.button("Predict Delay"):
    train_data = routes[routes["TrainNumber"].astype(str) == str(train_no)]
    if train_data.empty:
        st.error(f"Train number {train_no} not found in routes data")
    else:
        distance = train_data["Distance"].max()
        city_name = train_data["StationName"].iloc[0]
        departure_time_str = train_data["DepartureTime"].iloc[0]
        # Fetch weather and festival
        weather = get_weather(city_name, pd.to_datetime(date).date())
        festival = get_festival_impact(pd.to_datetime(date).date())
        if not festival:
            festival = "None"
        # Parse departure time
        try:
            departure_time = pd.to_datetime(departure_time_str, format="%H:%M:%S")
        except ValueError:
            departure_time = pd.to_datetime(departure_time_str, format="%H:%M")
        hour = departure_time.hour
        if 4 <= hour < 9:
            time_of_day = "Morning"
        elif 9 <= hour < 18:
            time_of_day = "Day"
        elif 18 <= hour < 22:
            time_of_day = "Evening"
        else:
            time_of_day = "Night"
        # Prepare input
        input_df = pd.DataFrame([{"Distance": distance, "Weather": weather, "FestivalImpact": festival, "TimeOfDay": time_of_day}])
        # One-hot encode
        training_data = pd.read_csv(os.path.join("datasets", "processed", "final_clean_dataset.csv"))
        training_data = pd.get_dummies(training_data, columns=["FestivalImpact", "Weather", "TimeOfDay"], drop_first=True)
        X_train_columns = training_data.drop(columns=["DelayMinutes", "Date", "StationName", "StationCode", "ArrivalTime", "DepartureTime"]).columns
        input_df = pd.get_dummies(input_df)
        for col in X_train_columns:
            if col not in input_df.columns:
                input_df[col] = 0
        input_df = input_df[X_train_columns]
        # Predict
        prediction = model.predict(input_df)[0]
        st.success(f"Predicted Delay: {prediction:.2f} minutes")
        st.write("---")
        st.write("**Inputs Used:**")
        st.json({
            "TrainNumber": train_no,
            "Date": str(date),
            "Distance": distance,
            "Weather": weather,
            "FestivalImpact": festival,
            "TimeOfDay": time_of_day
        })
