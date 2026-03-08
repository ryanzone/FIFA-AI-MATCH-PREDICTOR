"""Player Scout feature — search, radar chart, growth tracker."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import load_players, RADAR_ATTRS, RADAR_LABELS


def render():
    st.header("🔍 Player Scout")
    st.caption("Search any player · Radar chart · Historical growth (2017-2023)")

    p_latest = load_players("23")
    names = sorted(p_latest["short_name"].dropna().unique())
    pick = st.selectbox("Search player", [""] + names)

    if not pick:
        return

    row = p_latest[p_latest["short_name"] == pick]
    if row.empty:
        st.warning("Player not found.")
        return
    p = row.iloc[0]

    # KPI row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall", int(p["overall"]) if pd.notna(p["overall"]) else "–")
    c2.metric("Potential", int(p["potential"]) if pd.notna(p["potential"]) else "–")
    c3.metric("Value", f"€{p['value_eur']/1e6:.1f}M" if pd.notna(p["value_eur"]) and p["value_eur"] > 0 else "–")
    c4.metric("Wage", f"€{p['wage_eur']/1e3:.0f}K" if pd.notna(p["wage_eur"]) and p["wage_eur"] > 0 else "–")

    st.markdown(
        f"**Club:** {p.get('club_name','–')} · **Nation:** {p.get('nationality_name','–')} · "
        f"**Pos:** {p.get('player_positions','–')} · **Age:** {int(p['age']) if pd.notna(p.get('age')) else '–'}"
    )
    st.markdown("---")

    left, right = st.columns(2)

    # Radar
    with left:
        st.subheader("Attribute Radar")
        vals = [float(p.get(a, 0)) if pd.notna(p.get(a)) else 0 for a in RADAR_ATTRS]
        fig = go.Figure(go.Scatterpolar(
            r=vals + [vals[0]], theta=RADAR_LABELS + [RADAR_LABELS[0]],
            fill="toself", fillcolor="rgba(0,180,216,0.25)",
            line=dict(color="#00b4d8", width=2),
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(range=[0, 100])),
            margin=dict(l=40, r=40, t=20, b=20), height=350,
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Growth
    with right:
        st.subheader("Growth 2017 → 2023")
        history = []
        for y in range(17, 24):
            try:
                df_y = load_players(str(y))
                p_row = df_y[df_y["short_name"] == pick]
                if not p_row.empty:
                    history.append((y, p_row.iloc[0]))
            except Exception:
                pass
                
        if len(history) < 2:
            st.info("Not enough historical data for this player.")
        else:
            fig = go.Figure()
            x_vals = [f"20{y}" for y, _ in history]
            
            # Plot OVR and Potential
            ovrs = [float(r.get("overall", 0)) if pd.notna(r.get("overall")) else 0 for _, r in history]
            pots = [float(r.get("potential", 0)) if pd.notna(r.get("potential")) else 0 for _, r in history]
            
            fig.add_trace(go.Scatter(x=x_vals, y=ovrs, mode='lines+markers', name='Overall', line=dict(color='#00b4d8', width=3)))
            fig.add_trace(go.Scatter(x=x_vals, y=pots, mode='lines+markers', name='Potential', line=dict(color='#0077b6', width=2, dash='dot')))
            
            fig.update_layout(
                yaxis=dict(range=[0, 100]),
                margin=dict(l=0, r=0, t=20, b=0), height=350,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
            )
            st.plotly_chart(fig, use_container_width=True)

            d1, d2 = st.columns(2)
            first_r, last_r = history[0][1], history[-1][1]
            ovr_f = float(first_r["overall"]) if pd.notna(first_r.get("overall")) else 0
            ovr_l = float(last_r["overall"]) if pd.notna(last_r.get("overall")) else 0
            d1.metric(f"OVR Change (20{history[0][0]}->20{history[-1][0]})", f"{ovr_l:.0f}", f"{ovr_l-ovr_f:+.0f}")
            
            val_f = float(first_r["value_eur"]) if pd.notna(first_r.get("value_eur")) else 0
            val_l = float(last_r["value_eur"]) if pd.notna(last_r.get("value_eur")) else 0
            d2.metric(f"Value Change", f"€{val_l/1e6:.1f}M", f"{(val_l-val_f)/1e6:+.1f}M")
