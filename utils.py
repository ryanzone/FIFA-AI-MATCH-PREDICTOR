"""Shared data loaders and constants for FIFA AI Predictor."""
import streamlit as st
import pandas as pd
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

RADAR_ATTRS = ["pace", "shooting", "passing", "dribbling", "defending", "physic"]
RADAR_LABELS = ["Pace", "Shooting", "Passing", "Dribbling", "Defending", "Physical"]


@st.cache_data
def load_matches():
    return pd.read_csv(os.path.join(DATA_DIR, "matches_cleaned.csv"))


@st.cache_data
def load_players(year: str):
    df = pd.read_csv(
        os.path.join(DATA_DIR, "FIFA_DATA", "cleaned", f"fifa{year}_cleaned.csv"), low_memory=False
    )
    
    # Rename columns to match old app schema
    rmap = {
        "Name": "short_name", "Overall": "overall", "Potential": "potential",
        "Value": "value_eur", "Wage": "wage_eur", "Nationality": "nationality_name",
        "Position": "player_positions", "Club": "club_name", "Age": "age"
    }
    df = df.rename(columns=rmap)
    
    # Strip HTML tags from positions (e.g., <span class="pos pos9">ST</span> -> ST)
    if "player_positions" in df.columns and df["player_positions"].dtype == object:
        df["player_positions"] = df["player_positions"].str.replace(r'<[^>]+>', '', regex=True)
    
    # Compute radar attributes if they don't exist
    def _avg(cols):
        valid = [c for c in cols if c in df.columns]
        return df[valid].mean(axis=1) if valid else pd.Series([0]*len(df), index=df.index)

    if "pace" not in df.columns:
        df["pace"] = _avg(["SprintSpeed", "Acceleration"])
        df["shooting"] = _avg(["Finishing", "ShotPower", "LongShots"])
        df["passing"] = _avg(["ShortPassing", "LongPassing", "Vision"])
        df["dribbling"] = _avg(["Dribbling", "BallControl", "Agility"])
        df["defending"] = _avg(["StandingTackle", "SlidingTackle", "Interceptions"])
        df["physic"] = _avg(["Strength", "Stamina", "Jumping"])
        
    return df
