import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Air Pollution Dashboard", layout="wide")
st.title("🌫 Air Pollution Analysis Dashboard")

# -----------------------------
# Load Data
# -----------------------------
city_day = pd.read_csv("data/clean_city_data.csv")
station_full = pd.read_csv("data/clean_station_data.csv")

city_day["Date"] = pd.to_datetime(city_day["Date"])

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Filters")

cities = st.sidebar.multiselect(
    "Select Cities",
    options=city_day["City"].unique(),
    default=city_day["City"].unique(),
    help="Type to search cities"
)

years = st.sidebar.multiselect(
    "Select Year(s)",
    sorted(city_day["Year"].unique()),
    default=sorted(city_day["Year"].unique())
)

seasons = st.sidebar.multiselect(
    "Select Season(s)",
    city_day["Season"].unique(),
    default=city_day["Season"].unique()
)

min_aqi, max_aqi = st.sidebar.slider(
    "AQI Range",
    int(city_day["AQI"].min()),
    int(city_day["AQI"].max()),
    (int(city_day["AQI"].min()), int(city_day["AQI"].max()))
)

# Filter data
filtered = city_day[
    (city_day["City"].isin(cities)) &
    (city_day["Year"].isin(years)) &
    (city_day["Season"].isin(seasons)) &
    (city_day["AQI"] >= min_aqi) &
    (city_day["AQI"] <= max_aqi)
].copy()

# -----------------------------
# KPI Metrics
# -----------------------------
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Average AQI", round(filtered["AQI"].mean(), 2))
col2.metric("Max AQI", round(filtered["AQI"].max(), 2))
col3.metric("Cities", filtered["City"].nunique())
col4.metric("Total Records", len(filtered))

# -----------------------------
# AQI Trend Over Time (Smoothed)
# -----------------------------
st.subheader("AQI Trend Over Time (7-day Rolling Average)")

filtered = filtered.sort_values(["City", "Date"])
filtered["AQI_Smooth"] = filtered.groupby("City")["AQI"].transform(lambda x: x.rolling(7,1).mean())

# Show only top 5 cities by average AQI to reduce clutter
top_cities = filtered.groupby("City")["AQI"].mean().sort_values(ascending=False).head(5).index
trend_data = filtered[filtered["City"].isin(top_cities)]

fig_trend = px.line(
    trend_data,
    x="Date",
    y="AQI_Smooth",
    color="City",
    title="Top 5 Cities AQI Trends"
)
st.plotly_chart(fig_trend, use_container_width=True)

# -----------------------------
# Two Column Charts
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("AQI Category Distribution")
    fig_cat = px.histogram(
        filtered,
        x="AQI_Category",
        color="AQI_Category",
        category_orders={"AQI_Category": ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]}
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with col2:
    st.subheader("Seasonal AQI")
    season_avg = filtered.groupby("Season")["AQI"].mean().reindex(["Winter","Summer","Monsoon","Post-Monsoon"]).reset_index()
    fig_season = px.bar(
        season_avg,
        x="Season",
        y="AQI",
        title="Average AQI by Season"
    )
    st.plotly_chart(fig_season, use_container_width=True)

# -----------------------------
# PM2.5 vs AQI + Monthly AQI
# -----------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("PM2.5 vs AQI")
    fig_pm = px.scatter(
        filtered,
        x="PM2.5",
        y="AQI",
        color="City",
        title="PM2.5 vs AQI"
    )
    st.plotly_chart(fig_pm, use_container_width=True)

with col4:
    st.subheader("Monthly AQI Trend")
    monthly_avg = filtered.groupby("Month")["AQI"].mean().reset_index()
    fig_month = px.line(
        monthly_avg,
        x="Month",
        y="AQI",
        markers=True,
        title="Average Monthly AQI"
    )
    st.plotly_chart(fig_month, use_container_width=True)

# -----------------------------
# Top Polluted Cities
# -----------------------------
st.subheader("Top 10 Polluted Cities")
top10 = filtered.groupby("City")["AQI"].mean().sort_values(ascending=False).head(10).reset_index()
fig_top_cities = px.bar(
    top10,
    x="AQI",
    y="City",
    orientation="h",
    color="AQI",
    color_continuous_scale="Reds",
    title="Top 10 Most Polluted Cities"
)
st.plotly_chart(fig_top_cities, use_container_width=True)

# -----------------------------
# Top Polluted Stations
# -----------------------------
st.subheader("Top 10 Polluted Stations")
top_stations = station_full.groupby("StationId")["AQI"].mean().sort_values(ascending=False).head(10).reset_index()
fig_stations = px.bar(
    top_stations,
    x="StationId",
    y="AQI",
    color="AQI",
    color_continuous_scale="Oranges",
    title="Top 10 Most Polluted Stations"
)
st.plotly_chart(fig_stations, use_container_width=True)

# -----------------------------
# City AQI Map
# -----------------------------
st.subheader("Air Pollution Map (City AQI)")

city_coords = {
    "Delhi": [28.7041, 77.1025],
    "Mumbai": [19.0760, 72.8777],
    "Kolkata": [22.5726, 88.3639],
    "Chennai": [13.0827, 80.2707],
    "Bangalore": [12.9716, 77.5946],
    "Hyderabad": [17.3850, 78.4867],
    "Ahmedabad": [23.0225, 72.5714],
    "Pune": [18.5204, 73.8567],
    "Jaipur": [26.9124, 75.7873],
    "Lucknow": [26.8467, 80.9462]
}

coords_df = pd.DataFrame.from_dict(
    city_coords,
    orient="index",
    columns=["lat", "lon"]
).reset_index().rename(columns={"index":"City"})

map_data = filtered.groupby("City")["AQI"].mean().reset_index()
map_data = map_data.merge(coords_df, on="City", how="left")

fig_map = px.scatter_mapbox(
    map_data,
    lat="lat",
    lon="lon",
    size="AQI",
    color="AQI",
    hover_name="City",
    color_continuous_scale="Reds",
    size_max=40,
    zoom=3
)
fig_map.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig_map, use_container_width=True)