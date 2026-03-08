# ⚽ FIFA AI Predictor

Streamlit web app using machine learning to forecast football match outcomes, scout player attributes, and analyze year-over-year player performance.

## Features

- **Dashboard** — Key stats overview
- **Match Predictor** — AI-predicted outcome with score, confidence %, probability chart
- **Player Scout** — Search any player, radar chart, 2021→2022 growth tracker
- **Head-to-Head** — Side-by-side player comparison with overlapping radars
- **Player Progress** — League-wide 2021 vs 2022 trends, biggest improvers & decliners

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure

```
├── app.py                 # Main entry point (~50 lines)
├── utils.py               # Shared data loaders
├── features/
│   ├── match_predictor.py # Match outcome prediction
│   ├── player_scout.py    # Player search & radar
│   ├── head_to_head.py    # Player comparison
│   └── player_progress.py # 2021 vs 2022 trends
├── .streamlit/config.toml # Dark theme
├── FIFA_DATA/             # Official FIFA 17-23 data (raw & cleaned)
└── matches_cleaned.csv    # Match history data
```

## Tech Stack

Streamlit · Scikit-Learn · Plotly · Pandas · NumPy
