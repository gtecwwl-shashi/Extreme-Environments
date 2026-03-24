import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Extreme Physiology Cascade", layout="wide")

st.title("🏔️ vs 🌊 Oxygen Cascade: Extreme Environments")
st.markdown("""
How does the Oxygen Cascade change at the **Summit of Everest** or **30 Meters Underwater**?
Predict the values for the chosen scenario to unlock the units.
""")

# --- 1. Scenario Database ---
scenarios = {
    "Sea Level (Baseline)": {"pb": 101.3, "fio2": 0.21, "desc": "Standard 1 ATM environment."},
    "Mt. Everest Summit": {"pb": 33.7, "fio2": 0.21, "desc": "Extreme Hypoxia. PB is 1/3 of sea level."},
    "Deep Sea (30m Depth)": {"pb": 405.2, "fio2": 0.21, "desc": "Hyperbaric environment (4 ATM). Risk of Oxygen Toxicity."}
}

selected_env = st.sidebar.selectbox("Choose Environment", list(scenarios.keys()))
env = scenarios[selected_env]

# --- 2. Calculate Physiological Truth for Scenario ---
pb = env["pb"]
fio2 = env["fio2"]
# Humidification is always ~6.3 kPa at 37°C
p_trachea = fio2 * (pb - 6.3)
# Simplified Alveolar Gas (assuming PaCO2 5.3, RQ 0.8)
p_alveoli = p_trachea - (5.3 / 0.8)
# Arterial (A-a gradient ~1.5)
p_artery = p_alveoli - 1.5
# Venous/Mitochondria (Physiologically capped at lower limits)
p_vein = min(5.3, p_artery - 4.0)
p_mito = 1.2

truth_vals = [round(fio2 * pb, 1), round(p_trachea, 1), round(p_alveoli, 1), 
              round(p_artery, 1), round(p_vein, 1), round(p_mito, 1)]
stages = ["Atmosphere", "Trachea", "Alveoli", "Artery", "Vein", "Mitochondria"]

st.sidebar.write(f"**Current Barometric Pressure:** {pb} kPa")
st.sidebar.caption(env["desc"])

# --- 3. Interactive Inputs ---
st.subheader(f"Predict values for: {selected_env}")
user_vals = []
cols = st.columns(len(stages))

for i, stage in enumerate(stages):
    with cols[i]:
        u_val = st.number_input(f"{stage} (kPa)", min_value=0.0, value=0.0, step=0.1, key=f"v_{selected_env}_{i}")
        user_vals.append(u_val)

# --- 4. Validation & Reveal ---
if "revealed" not in st.session_state:
    st.session_state.revealed = False

if st.button("Submit Predictions"):
    st.session_state.revealed = True

# Filter for correct hits (within 0.8 kPa for extreme ranges)
revealed_points = [t if abs(u - t) <= 0.8 else None for u, t in zip(user_vals, truth_vals)]

# --- 5. Plotting ---
fig = go.Figure()

# User's Predicted Path
fig.add_trace(go.Scatter(
    x=stages, y=user_vals, name='Your Prediction',
    line=dict(color='#95a5a6', dash='dot', shape='hv'),
    marker=dict(size=8, symbol='x')
))

# Revealed Hits
if st.session_state.revealed:
    fig.add_trace(go.Scatter(
        x=stages, y=revealed_points, name='Correct Hits',
        mode='markers+text',
        text=[f"{v} kPa" if v is not None else "" for v in revealed_points],
        textposition="top center",
        marker=dict(size=15, color='#f39c12', symbol='diamond')
    ))

fig.update_layout(
    yaxis_title="PO2 (kPa)",
    template="plotly_white",
    yaxis=dict(range=[0, max(truth_vals) + 20]),
    height=550
)

st.plotly_chart(fig, use_container_width=True)

# --- 6. Teaching Context ---
if st.session_state.revealed:
    if selected_env == "Mt. Everest Summit":
        st.warning("⚠️ **Clinical Insight:** Notice the 'Alveolar' value. At this altitude, $P_A O_2$ is so low that even a small $CO_2$ level significantly displaces oxygen!")
    elif selected_env == "Deep Sea (30m Depth)":
        st.error("☢️ **Clinical Insight:** The $P_O2$ in the lungs is over 80 kPa. This exceeds the threshold for pulmonary oxygen toxicity if breathed for long periods.")
