"""Match Predictor feature — Win/Loss/Draw + score prediction."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from utils import load_matches


@st.cache_data
def _train_model():
    df = load_matches().copy()

    le_map = {}
    for col in ["venue", "opponent", "formation", "day"]:
        le = LabelEncoder()
        df[col + "_code"] = le.fit_transform(df[col].astype(str))
        le_map[col] = le

    res_enc = LabelEncoder()
    df["result_code"] = res_enc.fit_transform(df["result"])

    feats = [
        "venue_code", "opponent_code", "formation_code", "day_code",
        "xg", "xga", "poss", "gf", "ga", "sh", "sot", "dist",
        "fk", "pk", "pkatt", "attendance",
    ]
    X = df[feats].fillna(0)
    y = df["result_code"]
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    Xtr, Xte, ytr, yte = train_test_split(Xs, y, test_size=0.2, random_state=42)
    clf = RandomForestClassifier(n_estimators=200, random_state=42, max_depth=12)
    clf.fit(Xtr, ytr)
    acc = accuracy_score(yte, clf.predict(Xte))

    goal_reg = RandomForestRegressor(n_estimators=150, random_state=42, max_depth=10)
    goal_reg.fit(Xtr, df.loc[ytr.index, "gf"].values)

    return clf, goal_reg, le_map, scaler, res_enc, df, feats, acc


def render():
    st.header("⚔️ Match Predictor")
    st.caption("AI-powered outcome & scoreline forecasting")

    clf, goal_reg, le_map, scaler, res_enc, df, feats, acc = _train_model()
    st.markdown(f"Model accuracy: **{acc*100:.1f}%**")

    all_teams = sorted(set(df["team"].unique()) | set(df["opponent"].unique()))

    with st.form("match_form"):
        c1, c2 = st.columns(2)
        with c1:
            team_a = st.selectbox("Home Team", all_teams)
        with c2:
            team_b = st.selectbox("Away Team", all_teams, index=min(1, len(all_teams) - 1))
        go_btn = st.form_submit_button("⚡ Predict")

    if not go_btn:
        return
    if team_a == team_b:
        st.warning("Pick two different teams.")
        return

    with st.spinner("Predicting…"):
        avg = df.mean(numeric_only=True)
        a_stats = df[df["team"] == team_a].mean(numeric_only=True)
        b_stats = df[df["opponent"] == team_b].mean(numeric_only=True)
        if a_stats.isna().all():
            a_stats = avg
        if b_stats.isna().all():
            b_stats = avg

        sample = df.iloc[0:1].copy()
        for c in ["xg","xga","poss","gf","ga","sh","sot","dist","fk","pk","pkatt","attendance"]:
            va = a_stats[c] if not pd.isna(a_stats.get(c)) else avg[c]
            vb = b_stats[c] if not pd.isna(b_stats.get(c)) else avg[c]
            sample[c] = (va + vb) / 2

        for cat in ["venue", "opponent", "formation", "day"]:
            try:
                val = team_b if cat == "opponent" else str(sample[cat].values[0])
                sample[cat + "_code"] = le_map[cat].transform([val])[0]
            except (ValueError, KeyError):
                sample[cat + "_code"] = 0

        Xi = scaler.transform(sample[feats])
        pred = clf.predict(Xi)[0]
        proba = clf.predict_proba(Xi)[0]
        label = res_enc.inverse_transform([pred])[0]

        pg = max(0, round(goal_reg.predict(Xi)[0]))
        og = max(0, round(b_stats.get("ga", 1) if not pd.isna(b_stats.get("ga")) else 1))
        if label == "W":
            hg, ag = max(pg, og + 1), og
        elif label == "L":
            hg, ag = pg, max(og, pg + 1)
        else:
            hg, ag = pg, pg

    # Results
    st.markdown("---")
    r_map = {"W": "🏆 Home Win", "L": "❌ Away Win", "D": "🤝 Draw"}
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Result", r_map.get(label, label))
    mc2.metric("Score", f"{hg} – {ag}")
    mc3.metric("Confidence", f"{max(proba)*100:.1f}%")

    # Probability chart
    labels = [{"W": "Home Win", "L": "Away Win", "D": "Draw"}.get(l, l) for l in res_enc.classes_]
    fig = go.Figure(go.Bar(
        x=labels, y=proba,
        marker_color=["#ffd60a", "#ff6b6b", "#00b4d8"][:len(labels)],
        text=[f"{p*100:.1f}%" for p in proba], textposition="outside",
    ))
    fig.update_layout(
        yaxis=dict(range=[0, 1.15], title="Probability"),
        margin=dict(l=0, r=0, t=10, b=0), height=300,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)
