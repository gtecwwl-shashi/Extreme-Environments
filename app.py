import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Global Oxygen Cascade Challenge", layout="wide")

st.title("🌍 Global Oxygen Cascade Challenge")
st.markdown("Predict the $P_{O_2}$ (kPa) for different environments around the world.")

# --- 1. Scenario Database ---
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
# Everest has low CO2 (3.0) due to hyperventilation; others use 5.3
paco2 = 3.0 if "Everest" in selected_env else 5.3
p_alv = p_trach - (paco2 / 0.8)
# Step 4: Artery (A-a gradient ~1.5)
p_art = p_alv - 1.5
# Step 5: Mitochondria (Pasteur Point)
p_mito = 1.2 if p_art > 2.0 else 0.1

truth_vals = [max(0.1, round(v, 1)) for v in [p_atm, p_trach, p_alv, p_art, p_mito]]
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
    # This line is now fully closed and safe:
    revealed_points = [t if abs(u - t) <= 0.5 else None for u, t in zip(user_vals, truth_vals)]
    
    fig.add_trace(go.Scatter(
        x=stages, y=revealed_points, name='Correct Hits',
        mode='markers+text',
        text=[f"{v} kPa" if v is not None else "" for v in revealed_points],
        textposition="top center",
        marker=dict(size=18, color='#27ae60', symbol='diamond-tall', line=dict(width=2, color='white'))
    ))

    # Dynamic Y-axis scale
    max_range = max(truth_vals) + 15
    fig.update_layout(
        title=f"Verification: {selected_env}",
        yaxis_title="PO2 (kPa)",
        template="plotly_white",
        yaxis=dict(range=[0, max_range]),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- 5. Clinical Feedback ---
    score = sum(1 for v in revealed_points if v is not None)
    st.write(f"**Score:** {score}/5 Units Unlocked")
    
    if score == 5:
        st.balloons()
        st.success("Perfect! You've mastered this environment.")
    
    if "Everest" in selected_env:
        st.warning("⚠️ **Everest Insight:** Atmospheric $P_{O_2}$ is ~7.1 kPa. Once $H_{2}O$ and $CO_{2}$ displace oxygen, the Alveolar $P_{O_2}$ drops to ~3.3 kPa—the absolute limit of human survival.")
    elif "Deep Sea" in selected_env:
        st.error("☢️ **Deep Sea Insight:** At 30m, $P_{O_2}$ is ~85 kPa. Breathing this for long periods causes Pulmonary Oxygen Toxicity.")

if st.button("Reset Scenario"):
    st.rerun()
