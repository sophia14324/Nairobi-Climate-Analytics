# app.py

import streamlit as st
import pandas as pd
import requests
import datetime
import plotly.express as px
import osmnx as ox
import folium
from streamlit_folium import st_folium

AQICN_TOKEN = ""
LOCATION = "Nairobi"

st.set_page_config(page_title="Urban Climate Watch: Nairobi", layout="wide")
st.title("🌍 Urban Climate Watch – Nairobi")
st.write("Monitoring **temperature**, **air quality**, and **urban green zones** in Nairobi")

st.subheader("🌫️ Real-Time Air Quality in Nairobi")
try:
    response = requests.get(f"https://api.waqi.info/feed/{LOCATION}/?token={AQICN_TOKEN}")
    aqi_data = response.json()

    if aqi_data["status"] == "ok":
        aqi = aqi_data["data"]["aqi"]
        pm25 = aqi_data["data"]["iaqi"].get("pm25", {}).get("v", "N/A")
        st.metric("Current AQI", aqi)
        st.metric("PM2.5", pm25)
    else:
        st.warning("⚠ Could not fetch AQI data.")
except Exception as e:
    st.error(f"API error: {e}")

st.subheader("🌡️ Historical Temperature – Last 7 Days")

today = datetime.date.today()
start = today - datetime.timedelta(days=7)

params = {
    "latitude": -1.2921,
    "longitude": 36.8219,
    "start_date": start.isoformat(),
    "end_date": today.isoformat(),
    "hourly": "temperature_2m",
    "timezone": "auto"
}

temp_api = "https://archive-api.open-meteo.com/v1/archive"
res = requests.get(temp_api, params=params, timeout=10)
data = res.json()

if "hourly" in data:
    df_temp = pd.DataFrame(data["hourly"])
    df_temp["time"] = pd.to_datetime(df_temp["time"])
    fig_temp = px.line(df_temp, x="time", y="temperature_2m", title="Hourly Temperature in Nairobi (Past 7 Days)")
    st.plotly_chart(fig_temp, use_container_width=True)
else:
    st.warning("No temperature data available.")

st.subheader("🌿 Nairobi Green Spaces")

with st.spinner("Loading green zones..."):
    tags = {"leisure": "park"}
    graph = ox.features_from_place("Nairobi, Kenya", tags=tags)
    parks = graph[["geometry"]].dropna()

    m = folium.Map(location=[-1.2921, 36.8219], zoom_start=12)
    for _, row in parks.iterrows():
        folium.GeoJson(row["geometry"]).add_to(m)

    st_folium(m, width=700, height=450)

st.markdown("---")
st.write("Developed by [@sophia14324](https://github.com/sophia14324) • Data from Open-Meteo, AQICN, OpenStreetMap")
