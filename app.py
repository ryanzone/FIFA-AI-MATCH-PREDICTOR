import streamlit as st
from utils import load_matches, load_players

# ── Config ──
st.set_page_config(page_title="FIFA AI Predictor", page_icon="⚽", layout="wide")
st.title("⚽ FIFA AI Predictor")
st.caption("ML-powered match predictions, player scouting & analytics")

# ── Sidebar nav ──
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Dashboard", "⚔️ Match Predictor", "🔍 Player Scout", "📊 Head-to-Head", "📈 Player Progress"],
)

# ── Dashboard (inline — it's short) ──
if page == "🏠 Dashboard":
    matches = load_matches()
    
    st.subheader("Overview")
    year = st.selectbox("Season", [str(y) for y in range(17, 24)], index=6, format_func=lambda x: f"20{x}")
    p_df = load_players(year)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Matches Database", f"{len(matches):,}")
    c2.metric(f"Players (20{year})", f"{len(p_df):,}")
    top = p_df.sort_values("overall", ascending=False).iloc[0]
    c3.metric("Top Rated", top["short_name"], f"OVR {int(top['overall'])}")
    rich = p_df.sort_values("value_eur", ascending=False).iloc[0]
    c4.metric("Most Valuable", rich["short_name"], f"€{rich['value_eur']/1e6:.0f}M")

    st.markdown("---")
    st.subheader(f"Top 10 Players by Overall (20{year})")
    st.dataframe(
        p_df.sort_values("overall", ascending=False)
        .head(10)[["short_name", "club_name", "overall", "value_eur"]]
        .rename(columns={"short_name": "Name", "club_name": "Club", "overall": "OVR", "value_eur": "Value (€)"}),
        use_container_width=True, hide_index=True,
    )

# ── Feature pages (imported from features/) ──
elif page == "⚔️ Match Predictor":
    from features.match_predictor import render
    render()

elif page == "🔍 Player Scout":
    from features.player_scout import render
    render()

elif page == "📊 Head-to-Head":
    from features.head_to_head import render
    render()

elif page == "📈 Player Progress":
    from features.player_progress import render
    render()

# ── Footer ──
st.markdown("---")
st.caption("Built with Streamlit · Scikit-Learn · Plotly · Data from Kaggle")
