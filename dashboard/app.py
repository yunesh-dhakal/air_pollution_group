import streamlit as st
import pandas as pd
import plotly.express as px

# Page title
st.title("India Air Pollution Dashboard")

# Load dataset
city_day = pd.read_csv("data/city_day.csv")

# Convert date column
city_day["Date"] = pd.to_datetime(city_day["Date"])

# Sidebar filter
st.sidebar.header("Filter Options")

selected_city = st.sidebar.selectbox(
    "Select City",
    sorted(city_day["City"].dropna().unique())
)

# Filter dataset
filtered_data = city_day[city_day["City"] == selected_city]

st.subheader(f"Air Quality Data for {selected_city}")

# Show dataset preview
st.write(filtered_data.head())

# AQI Trend
st.subheader("AQI Trend Over Time")

fig1 = px.line(
    filtered_data,
    x="Date",
    y="AQI",
    title="AQI Trend"
)

st.plotly_chart(fig1)

# Pollutant comparison
st.subheader("Pollutant Levels Over Time")

pollutants = ["PM2.5","PM10","NO2","CO","SO2","O3"]

fig2 = px.line(
    filtered_data,
    x="Date",
    y=pollutants,
    title="Pollutant Trends"
)

st.plotly_chart(fig2)

# Average AQI by city
st.subheader("Average AQI by City")

city_avg = city_day.groupby("City")["AQI"].mean().reset_index()

fig3 = px.bar(
    city_avg,
    x="City",
    y="AQI",
    title="Average AQI by City"
)

st.plotly_chart(fig3)