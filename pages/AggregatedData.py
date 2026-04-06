import streamlit as st
import pandas as pd

from clients.SensorClient import get_aggregated_data
from models.SensorType import SensorType
from utils.Initialize import initialize
from utils.Sidebar import render_sidebar

# -----------------------
# Page Setup
# -----------------------
st.set_page_config(layout="wide")
st.session_state.page = "aggregated_data"

initialize()
render_sidebar()

st.title('📊 Aggregated Data')
st.caption('View aggregated environmental sensor statistics by region and sensor type.')

# -----------------------
# Filters
# -----------------------
st.subheader("Filters")

filter_cols = st.columns(4)

country = filter_cols[0].text_input("Country")
city = filter_cols[1].text_input("City")
start_time = filter_cols[2].datetime_input("Start", value=None)
end_time = filter_cols[3].datetime_input("End", value=None)

submit = st.button("Fetch Data", width='stretch')

st.divider()

# -----------------------
# Label Mapping (ENUM-BASED)
# -----------------------
sensor_labels = {
    SensorType.AIR_QUALITY: ("🌬️", "Air Quality", "AQI"),
    SensorType.NOISE: ("🔊", "Noise", "dB"),
    SensorType.TEMPERATURE: ("🌡️", "Temperature", "°C"),
    SensorType.HUMIDITY: ("💧", "Humidity", "%"),
}

# -----------------------
# Fetch + Display
# -----------------------
if submit:

    start_ts = int(start_time.timestamp()) if start_time else None
    end_ts = int(end_time.timestamp()) if end_time else None

    try:
        agg = get_aggregated_data(
            country=country or None,
            city=city or None,
            start_time=start_ts,
            end_time=end_ts
        )
    except Exception:
        st.error("Failed to fetch aggregated data.")
        st.stop()

    if not agg:
        st.info("No aggregated data available.")
        st.stop()

    # -----------------------
    # Summary Cards
    # -----------------------
    st.subheader("📈 Summary Statistics")

    cols = st.columns(len(agg))

    for i, (sensor_type_key, stats) in enumerate(agg.items()):
        icon, label, unit = sensor_labels.get(
            sensor_type_key,
            ("📡", sensor_type_key.value.title(), "")
        )

        with cols[i]:
            st.metric(
                label=f"{icon} {label} — Mean",
                value=f"{stats.mean} {unit}",
                help=f"Median: {stats.median} | Mode: {stats.mode}"
            )
            st.caption(
                f"Median: **{stats.median}** · Mode: **{stats.mode}**"
            )

    st.divider()

    # -----------------------
    # Detail Table
    # -----------------------
    st.subheader("🔍 Breakdown by Sensor Type")

    rows = []
    for sensor_type_key, stats in agg.items():
        icon, label, unit = sensor_labels.get(
            sensor_type_key,
            ("📡", sensor_type_key.value.title(), "")
        )

        rows.append({
            "Sensor Type": f"{icon} {label}",
            "Unit": unit,
            "Mean": stats.mean,
            "Median": stats.median,
            "Mode": stats.mode,
        })

    table_df = pd.DataFrame(rows)
    st.dataframe(table_df, width="stretch", hide_index=True)

    st.divider()

    # -----------------------
    # Bar Chart
    # -----------------------
    st.subheader("📊 Average Measurements by Sensor Type")

    chart_data = {
        sensor_labels.get(k, ("📡", k.value.title(), ""))[1]: v.mean
        for k, v in agg.items()
    }

    chart_df = pd.DataFrame.from_dict(
        chart_data, orient="index", columns=["Mean"]
    )

    st.bar_chart(chart_df)

else:
    st.info("Apply filters above and click **Fetch Data** to view aggregated statistics.")