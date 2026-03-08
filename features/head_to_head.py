"""Head-to-Head comparison feature."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import load_players, RADAR_ATTRS, RADAR_LABELS


def render():
    st.header("📊 Head-to-Head")
    st.caption("Compare two players side-by-side in any season")

    year = st.selectbox("Season", [str(y) for y in range(17, 24)], index=6, format_func=lambda x: f"20{x}")
    p_df = load_players(year)
    names = sorted(p_df["short_name"].dropna().unique())

    c1, c2 = st.columns(2)
    with c1:
        name_a = st.selectbox("Player A", names, index=0)
    with c2:
        name_b = st.selectbox("Player B", names, index=min(1, len(names) - 1))

    if name_a == name_b:
        st.warning("Pick two different players.")
        return

    pa = p_df[p_df["short_name"] == name_a].iloc[0]
    pb = p_df[p_df["short_name"] == name_b].iloc[0]

    # Info cards
    ic1, ic2 = st.columns(2)
    for col, pl, nm in [(ic1, pa, name_a), (ic2, pb, name_b)]:
        with col:
            st.subheader(nm)
            st.markdown(f"**Club:** {pl.get('club_name','–')} · **Pos:** {pl.get('player_positions','–')}")
            m1, m2 = st.columns(2)
            ovr = int(pl["overall"]) if pd.notna(pl.get("overall")) else 0
            val = pl["value_eur"] if pd.notna(pl.get("value_eur")) else 0
            m1.metric("Overall", ovr)
            m2.metric("Value", f"€{val/1e6:.1f}M" if val else "–")

    st.markdown("---")

    # Overlapping radar
    va = [float(pa.get(a, 0)) if pd.notna(pa.get(a)) else 0 for a in RADAR_ATTRS]
    vb = [float(pb.get(a, 0)) if pd.notna(pb.get(a)) else 0 for a in RADAR_ATTRS]
    labels_c = RADAR_LABELS + [RADAR_LABELS[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=va + [va[0]], theta=labels_c, fill="toself",
        fillcolor="rgba(0,180,216,0.2)", line=dict(color="#00b4d8", width=2), name=name_a,
    ))
    fig.add_trace(go.Scatterpolar(
        r=vb + [vb[0]], theta=labels_c, fill="toself",
        fillcolor="rgba(255,214,10,0.2)", line=dict(color="#ffd60a", width=2), name=name_b,
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(range=[0, 100])),
        margin=dict(l=50, r=50, t=20, b=50), height=420,
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Stat bars
    attrs = RADAR_ATTRS + ["overall", "potential"]
    lbls = RADAR_LABELS + ["Overall", "Potential"]
    av = [float(pa.get(a, 0)) if pd.notna(pa.get(a)) else 0 for a in attrs]
    bv = [float(pb.get(a, 0)) if pd.notna(pb.get(a)) else 0 for a in attrs]

    fig = go.Figure()
    fig.add_trace(go.Bar(y=lbls, x=av, name=name_a, orientation="h", marker_color="#00b4d8",
                         text=[f"{v:.0f}" for v in av], textposition="auto"))
    fig.add_trace(go.Bar(y=lbls, x=bv, name=name_b, orientation="h", marker_color="#ffd60a",
                         text=[f"{v:.0f}" for v in bv], textposition="auto"))
    fig.update_layout(
        barmode="group", xaxis=dict(range=[0, 100]),
        margin=dict(l=0, r=20, t=10, b=0), height=360,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=1.08, x=0.5, xanchor="center"),
    )
    st.plotly_chart(fig, use_container_width=True)

    aw = sum(1 for a, b in zip(av, bv) if a > b)
    bw = sum(1 for a, b in zip(av, bv) if b > a)
    st.markdown(f"**Verdict:** {name_a} wins **{aw}** · {name_b} wins **{bw}** · **{len(av)-aw-bw}** tied")
