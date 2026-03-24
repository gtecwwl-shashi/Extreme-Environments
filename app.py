import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Global Oxygen Cascade Challenge", layout="wide")

st.title("🌍 Global Oxygen Cascade Challenge")
st.markdown("Predict the $P_O2$ (kPa) for different environments around the world.")

# --- 1. Scenario Database ---
# We define the Barometric Pressure (PB) for each location
scenarios = {
    "Sea Level (Baseline)": {"pb": 101.3, "fio2": 0.21, "desc": "Standard 1 ATM. Oxygen is abundant."},
    "Mt. Everest Summit": {"pb": 33.7, "fio2": 0.21, "desc": "Extreme Hypoxia. PB is only 1/3 of sea level!"},
    "Deep Sea (30m Depth)": {"pb": 405.2, "fio2": 0.21, "desc": "Hyperbaric. 4 ATM of pressure. Risk of O2 toxicity."}
}

selected_env = st.sidebar.selectbox("Choose Your Environment:", list(scenarios.keys()))
env = scenarios[selected_env]

# --- 2. Calculate the 'True' Physiological Staircase ---
pb = env["pb"]
fio_val = env["fio2"]

# Step 1: Atmosphere
p_atm = fio_val * pb
# Step 2: Trachea (Humidification -6.3 kPa)
p_trach = fio_val * (pb - 6.3)
# Step 3: Alveoli (Alveolar Gas Equation - RQ 0.8)
# We assume PaCO2 is 5.3 at Sea/Deep, but 3.0 on Everest due to hyperventilation
paco2 = 3.0 if "Everest" in selected_env else 5.3
p_alv = p_trach - (paco2 / 0.8)
# Step 4: Artery (A-a gradient ~1.5)
p_art = p_alv - 1.5
# Step 5: Mitochondria (Pasteur Point)
p_mito = 1.2 if p_art > 2.0 else 0.1

truth_vals = [max(0, round(v, 1)) for v in [p_atm, p_trach, p_alv, p_art, p_mito]]
stages = ["Atmosphere", "Trachea", "Alveoli", "Artery", "Mitochondria"]

# --- 3. The Quiz Interface ---
st.subheader(f"📍 Location: {selected_env}")
st.info(f"Setting: {env['desc']} (PB = {pb} kPa)")

user_vals = []
cols = st.columns(len(stages))

for i, stage in enumerate(stages):
    with cols[i]:
        u_val = st.number_input(f"{stage} (kPa)", min_value=0.0, value=0.0, step=0.1, key=f"quiz_{selected_env}_{i}")
        user_vals.append(u_val)

# --- 4. Validation & Reveal ---
if st.button("Submit & Verify Results"):
    fig = go.Figure()

    # User's Predicted Path (Gray Dashed)
    fig.add_trace(go.Scatter(
        x=stages, y=user_vals, name='Your Prediction',
        line=dict(color='#bdc3c7', dash='dot', shape='hv'),
        marker=dict(size=8, symbol='x')
    ))

    # Strict Reveal Logic (Only show if within 0.5 kPa)
    revealed_points = [t if abs(u - t) <=
