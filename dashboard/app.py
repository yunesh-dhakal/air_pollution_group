import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Air Pollution Dashboard", layout="wide")

st.title("🌫 Air Pollution Analysis Dashboard")

# Load data
city_day = pd.read_csv("data/clean_city_data.csv")
station_full = pd.read_csv("data/clean_station_data.csv")

city_day["Date"] = pd.to_datetime(city_day["Date"])

# Sidebar filters

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


filtered = city_day[
    (city_day["City"].isin(cities)) &
    (city_day["Year"].isin(years)) &
    (city_day["Season"].isin(seasons)) &
    (city_day["AQI"] >= min_aqi) &
    (city_day["AQI"] <= max_aqi)
]


# KPI METRICS


st.subheader("Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Average AQI", round(filtered["AQI"].mean(), 2))
col2.metric("Max AQI", round(filtered["AQI"].max(), 2))
col3.metric("Cities", filtered["City"].nunique())
col4.metric("Total Records", len(filtered))


# AQI Trend


st.subheader("AQI Trend Over Time")

fig = px.line(
    filtered,
    x="Date",
    y="AQI",
    color="City"
)

st.plotly_chart(fig, use_container_width=True)


# TWO COLUMN LAYOUT


col1, col2 = st.columns(2)

with col1:

    st.subheader("AQI Category Distribution")

    fig2 = px.histogram(
        filtered,
        x="AQI_Category",
        color="AQI_Category"
    )

    st.plotly_chart(fig2, use_container_width=True)

with col2:

    st.subheader("Seasonal AQI")

    season_avg = filtered.groupby("Season")["AQI"].mean().reset_index()

    fig3 = px.bar(
        season_avg,
        x="Season",
        y="AQI"
    )

    st.plotly_chart(fig3, use_container_width=True)


# SCATTER + MONTHLY


col3, col4 = st.columns(2)

with col3:

    st.subheader("PM2.5 vs AQI")

    fig4 = px.scatter(
        filtered,
        x="PM2.5",
        y="AQI",
        color="City"
    )

    st.plotly_chart(fig4, use_container_width=True)

with col4:

    st.subheader("Monthly AQI Trend")

    monthly = filtered.groupby("Month")["AQI"].mean().reset_index()

    fig6 = px.line(
        monthly,
        x="Month",
        y="AQI",
        markers=True
    )

    st.plotly_chart(fig6, use_container_width=True)


# TOP POLLUTED CITIES


st.subheader("Top Polluted Cities")

top10 = filtered.groupby("City")["AQI"].mean().sort_values(ascending=False).head(10).reset_index()

fig5 = px.bar(
    top10,
    x="AQI",
    y="City",
    orientation="h"
)

st.plotly_chart(fig5, use_container_width=True)


# STATION ANALYSIS


st.subheader("Top Polluted Stations")

top_stations = station_full.groupby("StationId")["AQI"].mean().sort_values(ascending=False).head(10).reset_index()

fig8 = px.bar(
    top_stations,
    x="StationId",
    y="AQI"
)

st.plotly_chart(fig8, use_container_width=True)



# CITY AQI MAP

st.subheader("Air Pollution Map (City AQI)")

# City coordinates dictionary
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
).reset_index()
coords_df.rename(columns={"index": "City"}, inplace=True)


map_data = filtered.groupby("City")["AQI"].mean().reset_index()
map_data = map_data.merge(coords_df, on="City", how="left")

# Plot map
fig_map = px.scatter_map(
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

fig_map.update_layout(
    mapbox_style="carto-positron",
    margin={"r":0,"t":0,"l":0,"b":0}
)

st.plotly_chart(fig_map, width='stretch')  