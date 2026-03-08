"""Player Progress feature — 2021 vs 2022 trends."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import load_players, RADAR_ATTRS, RADAR_LABELS


def render():
    st.header("📈 Player Progress")
    st.caption("Custom league-wide trends & individual growth (2017-2023)")

    c_y1, c_y2 = st.columns(2)
    y1 = c_y1.selectbox("Start Season", [str(y) for y in range(17, 24)], index=4, format_func=lambda x: f"20{x}")
    y2 = c_y2.selectbox("End Season", [str(y) for y in range(17, 24)], index=5, format_func=lambda x: f"20{x}")
    p21, p22 = load_players(y1), load_players(y2)

    # Filters
    fc1, fc2 = st.columns(2)
    with fc1:
        nats = sorted(set(p21["nationality_name"].dropna().unique()) | set(p22["nationality_name"].dropna().unique()))
        nat_f = st.multiselect("Nationality", nats)
    with fc2:
        poss = sorted(set(p21["player_positions"].dropna().unique()) | set(p22["player_positions"].dropna().unique()))
        pos_f = st.multiselect("Position", poss)

    if nat_f:
        p21 = p21[p21["nationality_name"].isin(nat_f)]
        p22 = p22[p22["nationality_name"].isin(nat_f)]
    if pos_f:
        p21 = p21[p21["player_positions"].isin(pos_f)]
        p22 = p22[p22["player_positions"].isin(pos_f)]
    if p21.empty or p22.empty:
        st.warning("No players match the selected filters.")
        return

    # Year-over-year KPIs
    st.markdown("---")
    ar21, ar22 = p21["overall"].mean(), p22["overall"].mean()
    av21, av22 = p21["value_eur"].mean(), p22["value_eur"].mean()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"Avg Rating '{(y1)}", f"{ar21:.1f}")
    m2.metric(f"Avg Rating '{(y2)}", f"{ar22:.1f}", f"{ar22-ar21:+.2f}")
    m3.metric(f"Avg Value '{(y1)}", f"€{av21/1e6:.2f}M")
    m4.metric(f"Avg Value '{(y2)}", f"€{av22/1e6:.2f}M", f"{(av22-av21)/1e6:+.2f}M")

    st.markdown("---")

    # Top 10 side-by-side
    left, right = st.columns(2)
    for col, df, yr in [(left, p21, f"20{y1}"), (right, p22, f"20{y2}")]:
        with col:
            st.subheader(f"Top 10 — {yr}")
            top = df.sort_values("overall", ascending=False).head(10)[["short_name","club_name","overall","value_eur"]].copy()
            top["value_eur"] = top["value_eur"].apply(lambda x: f"€{x/1e6:.1f}M" if pd.notna(x) and x > 0 else "–")
            top.columns = ["Name", "Club", "OVR", "Value"]
            st.dataframe(top, use_container_width=True, hide_index=True)

    # Rating distribution overlay
    st.markdown("---")
    st.subheader("Rating Distribution")
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=p21["overall"], name=f"20{y1}", marker_color="#0077b6", opacity=0.7, nbinsx=30))
    fig.add_trace(go.Histogram(x=p22["overall"], name=f"20{y2}", marker_color="#00b4d8", opacity=0.7, nbinsx=30))
    fig.update_layout(
        barmode="overlay", xaxis_title="Overall Rating", yaxis_title="Players",
        margin=dict(l=0, r=0, t=10, b=0), height=300,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Biggest improvers / decliners
    st.markdown("---")
    st.subheader("Biggest Movers")
    merged = pd.merge(
        p21[["short_name","overall","value_eur"]],
        p22[["short_name","overall","value_eur"]],
        on="short_name", suffixes=("_21","_22"),
    )
    merged["Δ Rating"] = merged["overall_22"] - merged["overall_21"]
    merged["Δ Value"] = merged["value_eur_22"] - merged["value_eur_21"]

    t1, t2 = st.tabs(["📈 Improvers", "📉 Decliners"])
    for tab, asc in [(t1, False), (t2, True)]:
        with tab:
            view = merged.sort_values("Δ Rating", ascending=asc).head(15).copy()
            view["Δ Value"] = view["Δ Value"].apply(lambda x: f"€{x/1e6:+.1f}M" if pd.notna(x) else "–")
            disp = view[["short_name","overall_21","overall_22","Δ Rating","Δ Value"]]
            disp.columns = ["Player",f"OVR '{y1}",f"OVR '{y2}","Δ Rating","Δ Value"]
            st.dataframe(disp, use_container_width=True, hide_index=True)
