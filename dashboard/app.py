import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Air Pollution Analysis Dashboard")

# Load cleaned datasets
city_day = pd.read_csv("data/clean_city_data.csv")
station_full = pd.read_csv("data/clean_station_data.csv")

city_day["Date"] = pd.to_datetime(city_day["Date"])

# Sidebar filters
st.sidebar.header("Filters")

cities = st.sidebar.multiselect(
    "Select Cities",
    city_day["City"].unique(),
    default=city_day["City"].unique()
)

filtered = city_day[city_day["City"].isin(cities)]

# Overview Metrics
st.subheader("Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Average AQI", round(filtered["AQI"].mean(),2))
col2.metric("Maximum AQI", round(filtered["AQI"].max(),2))
col3.metric("Cities", filtered["City"].nunique())

# AQI Trend
st.subheader("AQI Trend Over Time")

fig = px.line(
    filtered,
    x="Date",
    y="AQI",
    color="City"
)

st.plotly_chart(fig, use_container_width=True)

# AQI Category Distribution
st.subheader("AQI Category Distribution")

fig2 = px.histogram(
    filtered,
    x="AQI_Category",
    color="AQI_Category"
)

st.plotly_chart(fig2, use_container_width=True)

# Seasonal Pollution
st.subheader("Seasonal AQI")

season_avg = filtered.groupby("Season")["AQI"].mean().reset_index()

fig3 = px.bar(
    season_avg,
    x="Season",
    y="AQI"
)

st.plotly_chart(fig3, use_container_width=True)

# PM2.5 vs AQI
st.subheader("PM2.5 vs AQI")

fig4 = px.scatter(
    filtered,
    x="PM2.5",
    y="AQI",
    color="City"
)

st.plotly_chart(fig4, use_container_width=True)

# Top polluted cities
st.subheader("Top Polluted Cities")

top10 = filtered.groupby("City")["AQI"].mean().sort_values(ascending=False).head(10).reset_index()

fig5 = px.bar(
    top10,
    x="AQI",
    y="City",
    orientation="h"
)

st.plotly_chart(fig5, use_container_width=True)

# Monthly trend
st.subheader("Monthly AQI Trend")

monthly = filtered.groupby("Month")["AQI"].mean().reset_index()

fig6 = px.line(
    monthly,
    x="Month",
    y="AQI",
    markers=True
)

st.plotly_chart(fig6, use_container_width=True)

# Station level pollution
st.subheader("Station Level Pollution")

station_city = station_full.groupby("City")["AQI"].mean().sort_values(ascending=False).reset_index()

fig7 = px.bar(
    station_city,
    x="City",
    y="AQI"
)

st.plotly_chart(fig7, use_container_width=True)

# Top polluted stations
st.subheader("Top 10 Polluted Stations")

top_stations = station_full.groupby("StationId")["AQI"].mean().sort_values(ascending=False).head(10).reset_index()

fig8 = px.bar(
    top_stations,
    x="StationId",
    y="AQI"
)

st.plotly_chart(fig8, use_container_width=True)