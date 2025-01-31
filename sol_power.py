# Code to obtain solar power from power project (NASA) website at chosen latitude, longitude, and time period.
# Selections can be made through interactive web app (Streamlit)

import streamlit as st
import requests
import pandas as pd
import matplotlib

# ✅ Set Matplotlib to use "Agg" (Non-GUI backend)
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

st.title("☀️ Solar Power Prediction with Time Series Plot")

# Automatically set the default start date to 1 year ago
today = datetime.today()
default_start = (today - timedelta(days=365)).strftime('%Y%m%d')
default_end = today.strftime('%Y%m%d')  # Today

# User Inputs
lat = st.number_input("Enter Latitude:", value=28.6139)
lon = st.number_input("Enter Longitude:", value=77.2090)
start_date = st.text_input("Start Date (YYYYMMDD):", default_start)
end_date = st.text_input("End Date (YYYYMMDD):", default_end)
panel_area = st.number_input("Solar Panel Area (m²):", value=10)
efficiency = st.slider("Panel Efficiency (%):", 10, 25, 18)

if st.button("Estimate Power"):
    api_url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=ALLSKY_SFC_SW_DWN&community=RE&longitude={lon}&latitude={lat}&start={start_date}&end={end_date}&format=JSON"
    
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        solar_radiation = data["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]

        # Convert to Pandas DataFrame for plotting
        df = pd.DataFrame(list(solar_radiation.items()), columns=['Date', 'Solar Radiation'])
        df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
        df.sort_values('Date', inplace=True)

        # 📌 Remove negative values
        df = df[df['Solar Radiation'] >= 0]  # Keep only non-negative values

        if df.empty:  # If all values were negative
            st.error("❌ No valid solar radiation data available after filtering out negative values.")
        else:
            # Estimate solar power
            total_radiation = df['Solar Radiation'].sum()
            avg_radiation = total_radiation / len(df)
            energy_output = (avg_radiation * panel_area * (efficiency / 100)) / 1000

            st.success(f"🌞 Estimated Power Output: {energy_output:.2f} kWh/day")

            # 📌 Time Series Plot of Solar Radiation
            st.subheader("📈 Time Series Plot of Daily Solar Radiation (Filtered)")
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(df['Date'].to_numpy(), df['Solar Radiation'].to_numpy(), marker='o', linestyle='-', color='b', label='Solar Radiation (W/m²)')
            ax.set_xlabel("Date")
            ax.set_ylabel("Solar Radiation (W/m²)")
            ax.set_title("Daily Solar Radiation Over Time")
            ax.legend()
            ax.grid(True)
            plt.xticks(rotation=45)

            st.pyplot(fig)  # Show the plot in Streamlit

    else:
        st.error("❌ Failed to fetch solar data. Please check inputs.")
