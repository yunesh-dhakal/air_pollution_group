import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Air Pollution Dashboard", layout="wide")

st.markdown("### 🌫 Air Pollution Dashboard")
st.caption("Interactive dashboard analyzing air pollution trends across major cities using AQI data.")

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    city_day = pd.read_csv("data/clean_city_data.csv")
    city_day["Date"] = pd.to_datetime(city_day["Date"])
    return city_day

city_day = load_data()

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Dashboard Filters")

cities = st.sidebar.multiselect(
    "Select Cities",
    sorted(city_day["City"].unique()),
    default=sorted(city_day["City"].unique())
)

year_range = st.sidebar.slider(
    "Year Range",
    int(city_day["Year"].min()),
    int(city_day["Year"].max()),
    (int(city_day["Year"].min()), int(city_day["Year"].max()))
)

filtered = city_day[
    (city_day["City"].isin(cities)) &
    (city_day["Year"] >= year_range[0]) &
    (city_day["Year"] <= year_range[1])
]

# -----------------------------
# KPI Metrics
# -----------------------------
m1, m2, m3, m4 = st.columns(4)

m1.metric("Average AQI", round(filtered["AQI"].mean(),1))

m2.metric(
    "Worst City AQI",
    round(filtered.groupby("City")["AQI"].mean().max(),1)
)

m3.metric(
    "Best City AQI",
    round(filtered.groupby("City")["AQI"].mean().min(),1)
)

m4.metric(
    "Cities Analyzed",
    filtered["City"].nunique()
)

# -----------------------------
# AQI Status Badge
# -----------------------------
avg_aqi = filtered["AQI"].mean()

def get_aqi_status(aqi):
    if aqi <= 50:
        return "Good", "#2ecc71"
    elif aqi <= 100:
        return "Satisfactory", "#27ae60"
    elif aqi <= 200:
        return "Moderate", "#f1c40f"
    elif aqi <= 300:
        return "Poor", "#e67e22"
    elif aqi <= 400:
        return "Very Poor", "#e74c3c"
    else:
        return "Severe", "#8e44ad"

status, color = get_aqi_status(avg_aqi)

st.markdown(
    f"""
    <div style="
        padding:8px;
        border-radius:8px;
        background-color:{color};
        color:white;
        text-align:center;
        font-weight:bold;
        font-size:16px;">
        Overall Air Quality: {status} (AQI {avg_aqi:.1f})
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Row 1 Charts
# -----------------------------
c1, c2, c3 = st.columns(3)

with c1:

    filtered = filtered.sort_values(["City","Date"])
    filtered["AQI_Smooth"] = filtered.groupby("City")["AQI"].transform(lambda x: x.rolling(7,1).mean())

    fig = px.line(
        filtered,
        x="Date",
        y="AQI_Smooth",
        color="City",
        title="AQI Trend Over Time"
    )

    fig.update_layout(height=250, margin=dict(l=10,r=10,t=40,b=10))
    st.plotly_chart(fig, use_container_width=True)

with c2:

    fig = px.histogram(
        filtered,
        x="AQI_Category",
        color="AQI_Category",
        title="AQI Category Distribution"
    )

    fig.update_layout(height=250, margin=dict(l=10,r=10,t=40,b=10))
    st.plotly_chart(fig, use_container_width=True)

with c3:

    season_avg = filtered.groupby("Season")["AQI"].mean().reset_index()

    fig = px.bar(
        season_avg,
        x="Season",
        y="AQI",
        title="Seasonal AQI"
    )

    fig.update_layout(height=250, margin=dict(l=10,r=10,t=40,b=10))
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Row 2 Charts
# -----------------------------
c4, c5, c6 = st.columns(3)

with c4:

    fig = px.scatter(
        filtered,
        x="PM2.5",
        y="AQI",
        color="City",
        title="PM2.5 vs AQI"
    )

    fig.update_layout(height=250, margin=dict(l=10,r=10,t=40,b=10))
    st.plotly_chart(fig, use_container_width=True)

with c5:

    monthly = filtered.groupby("Month")["AQI"].mean().reset_index()

    fig = px.line(
        monthly,
        x="Month",
        y="AQI",
        markers=True,
        title="Monthly AQI Trend"
    )

    fig.update_layout(height=250, margin=dict(l=10,r=10,t=40,b=10))
    st.plotly_chart(fig, use_container_width=True)

with c6:

    top10 = filtered.groupby("City")["AQI"].mean().sort_values(ascending=False).head(10).reset_index()

    fig = px.bar(
        top10,
        x="AQI",
        y="City",
        orientation="h",
        color="AQI",
        color_continuous_scale="Reds",
        title="Top Polluted Cities"
    )

    fig.update_layout(height=250, margin=dict(l=10,r=10,t=40,b=10))
    st.plotly_chart(fig, use_container_width=True)