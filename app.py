import requests
import streamlit as st
import numpy as np
import joblib
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os


st.set_page_config(page_title="IPL Score Predictor", page_icon="🏏", layout="centered")
st.markdown("""
<style>
@media (max-width: 768px) {
    .main {padding: 10px;}
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
.main {background-color: #0f172a;}
h1, h2, h3, label {color: white;}
</style>
""", unsafe_allow_html=True)


model = joblib.load("ipl_model.pkl")

teams = [
    'Chennai Super Kings',
    'Delhi Daredevils',
    'Kings XI Punjab',
    'Kolkata Knight Riders',
    'Mumbai Indians',
    'Rajasthan Royals',
    'Royal Challengers Bangalore',
    'Sunrisers Hyderabad'
]

FILE = "predictions.csv"

if not os.path.exists(FILE):
    pd.DataFrame(columns=["Time", "Batting", "Bowling", "Predicted Score"]).to_csv(FILE, index=False)


st.title("🏏 IPL First Innings Score Predictor")

bat_team = st.selectbox("Batting Team", teams)
bowl_team = st.selectbox("Bowling Team", teams)

overs = st.slider("Overs completed", 5.0, 20.0, 10.0, 0.1)
runs = st.number_input("Current runs", 0)
wickets = st.number_input("Wickets fallen", 0, 10)
runs_last_5 = st.number_input("Runs in last 5 overs", 0)
wickets_last_5 = st.number_input("Wickets in last 5 overs", 0, 10)


def encode(team):
    return [1 if t == team else 0 for t in teams]


if st.button("Predict Score"):

    bat_encoded = encode(bat_team)
    bowl_encoded = encode(bowl_team)

    input_data = np.array([
        bat_encoded + bowl_encoded +
        [overs, runs, wickets, runs_last_5, wickets_last_5]
    ])

    prediction = int(model.predict(input_data)[0])

    st.success(f"🏆 Predicted Final Score Range: {prediction-10} to {prediction+5}")


    df = pd.read_csv(FILE)

    new_row = {
        "Time": datetime.now(),
        "Batting": bat_team,
        "Bowling": bowl_team,
        "Predicted Score": prediction
    }

    df = pd.concat([df, pd.DataFrame([new_row])])
    df.to_csv(FILE, index=False)
    st.subheader("📈Match Progress")

    overs_list = [overs - 5, overs]
    runs_list = [runs_last_5, runs]

    plt.figure(figsize=(5,3))
    plt.plot(overs_list, runs_list)
    plt.xlabel("Overs")
    plt.ylabel("Runs")
    st.pyplot(plt)

    run_rate = runs / overs
    st.info(f"📊Current Run Rate: {run_rate:.2f}")
st.subheader("📊 Projected Run Growth")

overs_sim = np.linspace(overs, 20, 10)
runs_sim = runs + (overs_sim - overs) * (runs / overs)

plt.figure(figsize=(6,4))
plt.plot(overs_sim, runs_sim)
plt.xlabel("Overs")
plt.ylabel("Projected Runs")
st.pyplot(plt)


st.subheader("📡 Live Matches")

API_KEY = "d3cafcf3-93f2-42eb-a999-2fb0c8707097"

try:
    url = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"
    response = requests.get(url)
    data = response.json()

    for match in data["data"][:3]:
        st.markdown(
            f"""
            <div style='padding:15px;border-radius:12px;background:#1e293b;margin-bottom:10px'>
            <h4>{match["name"]}</h4>
            <p>Status: {match["status"]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

except:
    st.warning("Live data loading...")


