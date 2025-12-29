import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from skyfield.api import Star, load, wgs84
from datetime import datetime
from pytz import timezone

# --- SETUP ---
st.set_page_config(layout="wide")
st.title("✨ Stargaze: Night Sky View")

# 1. USER LOCATION (Hardcoded for prototype, can be dynamic later)
# Example: Amravati, Maharashtra (approx coordinates)
LAT = 20.9374
LON = 77.7796
st.sidebar.write(f"📍 Viewing from: {LAT}, {LON}")

# 2. TIME SETUP
# Get current time (Skyfield needs a specific time object)
ts = load.timescale()
t = ts.now()

# 3. THE "ENGINE" (Calculations)
@st.cache_data
def get_star_positions(lat, lon):
    # Load ephemeris data (positions of planets/earth)
    # 'de421.bsp' is a small file Skyfield downloads once
    planets = load('de421.bsp')
    earth = planets['earth']
    
    # Define the observer's location on Earth
    observer = earth + wgs84.latlon(lat, lon)
    
    # --- FAKE DATA FOR DEMO (Replace this block with pd.read_csv) ---
    # We generate 200 random stars to simulate a catalog
    df = pd.DataFrame({
        'name': [f'Star {i}' for i in range(200)],
        'ra_hours': np.random.uniform(0, 24, 200),
        'dec_degrees': np.random.uniform(-90, 90, 200),
        'magnitude': np.random.uniform(1, 6, 200) # 1 is bright, 6 is dim
    })
    # ---------------------------------------------------------------

    # Create Skyfield Star objects
    stars = Star(ra_hours=df['ra_hours'], dec_degrees=df['dec_degrees'])

    # CALCULATE: Where are these stars relative to the observer right now?
    astrometric = observer.at(t).observe(stars)
    alt, az, distance = astrometric.apparent().altaz()

    # Add results back to DataFrame
    df['altitude'] = alt.degrees
    df['azimuth'] = az.degrees
    
    # FILTER: Only show stars that are above the horizon (> 0 degrees altitude)
    visible_stars = df[df['altitude'] > 0].copy()
    
    return visible_stars

# Run the calculation
stars_df = get_star_positions(LAT, LON)

# 4. THE VISUALIZATION (2D Polar Plot)
# In astronomy maps:
# - Center of circle = Zenith (90 degrees altitude)
# - Edge of circle = Horizon (0 degrees altitude)
# So 'r' (radius) should be 90 - altitude.

fig = go.Figure()

fig.add_trace(go.Scatterpolar(
    r = 90 - stars_df['altitude'],  # Distance from center
    theta = stars_df['azimuth'],    # Angle (Compass direction)
    mode = 'markers',
    marker = dict(
        # Make brighter stars (lower mag) appear bigger
        size = 10 - stars_df['magnitude'], 
        color = 'white',
        opacity = 0.8
    ),
    hovertext = stars_df['name']
))

fig.update_layout(
    polar = dict(
        bgcolor = "black",
        radialaxis = dict(visible = False, range = [0, 90]), # Hide the grid rings
        angularaxis = dict(
            direction = "clockwise", # N -> E -> S -> W
            rotation = 90,           # Put North (0) at the top
            color = "white"
        )
    ),
    paper_bgcolor = "black",
    showlegend = False,
    height = 700
)

st.plotly_chart(fig, use_container_width=True)
