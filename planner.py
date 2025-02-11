import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ===============================
# Title and Introduction
# ===============================
st.title("Fueling Strategy & Energy Calculator")
st.markdown(
    """
This app helps you plan a fueling strategy for your run by estimating:

- **Race Time** (HH:MM:SS) from distance and speed.
- **Energy Reserve** throughout the race based on:
  - A rule‐of‐thumb estimate for glycogen energy: roughly **24 kcal/kg** from muscle glycogen plus about **400 kcal** from liver stores.
  - Energy expenditure approximated as **~1 kcal per kg per km**.
  - Fueling stops that add a fixed amount of calories.

**Important Caveats:**

- **Glycogen Energy Estimate:**  
  The values (24 kcal/kg from muscle and 400 kcal from liver) are widely used approximations (e.g. by Burke et al.) but actual stored glycogen varies with training, diet, and individual muscle mass.

- **Energy Expenditure:**  
  The ~1 kcal/kg/km estimate is a common starting point; however, running economy, terrain, pace, and biomechanics can cause considerable variation.

- **Fueling Strategy:**  
  Starting fueling at a set distance and then every fixed interval is a simplified method. In practice, timing and carbohydrate type should be adjusted based on gastrointestinal tolerance, pace, and environmental conditions. Research (Thomas et al., 2016; Jeukendrup, 2011) shows that planned carbohydrate ingestion during prolonged exercise helps delay fatigue.

Use this model as a guide to set up a preliminary fueling plan, then adjust through training feedback.
"""
)
st.latex(
    r"\text{Initial Energy} = 24 \times \text{Weight (kg)} + 400 \quad \text{kcal}"
)
st.latex(
    r"\text{Energy Reserve}(d) = \text{Initial Energy} + \Big(\text{Fueling Stops Up To } d \times \text{Fuel kcal}\Big) - \Big(\text{Weight (kg)} \times d\Big)"
)
st.latex(r"\text{Time} = \frac{\text{Distance (km)}}{\text{Speed (km/h)}}")

# ===============================
# Sidebar: Runner & Run Details
# ===============================
st.sidebar.header("Runner & Run Details")
distance = st.sidebar.number_input(
    "Race Distance (km)",
    min_value=1.0,
    value=42.0,
    step=0.1,
    help="Enter the total distance of your race (e.g., 42 km for a marathon).",
)
weight = st.sidebar.number_input(
    "Weight (kg)",
    min_value=1.0,
    value=70.0,
    step=0.5,
    help="Enter your body weight in kilograms.",
)
speed = st.sidebar.number_input(
    "Speed (km/h)",
    min_value=0.1,
    value=10.0,
    step=0.1,
    help="Enter your average running speed in km/h.",
)

# ===============================
# Sidebar: Fueling Plan Details
# ===============================
st.sidebar.header("Fueling Plan Details")
fuel_interval = st.sidebar.number_input(
    "Fueling Interval (km)",
    min_value=0.1,
    value=4.0,
    step=0.1,
    help="Distance between fueling stops.",
)
fuel_start = st.sidebar.number_input(
    "Start Fueling at (km)",
    min_value=0.0,
    value=5.0,
    step=0.1,
    help=(
        "Distance at which fueling begins. A typical recommendation is to start refueling once glycogen stores begin to decline."
    ),
)
fuel_kcal = st.sidebar.number_input(
    "Calories per Fueling Stop (kcal)",
    min_value=1.0,
    value=87.0,
    step=1.0,
    help="Calories provided by each fueling stop (e.g., from a carb gel).",
)

# ===============================
# Calculations
# ===============================
# 1. Race Time Calculation in HH:MM:SS
total_time_hours = distance / speed  # time in hours
total_time_seconds = total_time_hours * 3600
hours = int(total_time_seconds // 3600)
minutes = int((total_time_seconds % 3600) // 60)
seconds = int(total_time_seconds % 60)
formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# 2. Energy Calculations
# Initial energy: rule-of-thumb glycogen estimate (24 kcal/kg + 400 kcal).
initial_energy = weight * 24 + 400  # in kcal
# Total energy expenditure (approximation): 1 kcal per kg per km.
total_calories_burned = weight * distance

# 3. Determine Fueling Stops
if fuel_start < distance:
    fueling_points = np.arange(fuel_start, distance, fuel_interval)
else:
    fueling_points = np.array([])

# Create a distance array for plotting.
d_points = np.linspace(0, distance, 500)
# Compute number of fueling stops up to each point.
stops_up_to_d = np.where(
    d_points < fuel_start, 0, np.floor((d_points - fuel_start) / fuel_interval) + 1
)
# Energy reserve at each distance.
energy_points = initial_energy + stops_up_to_d * fuel_kcal - weight * d_points

if fuel_start < distance:
    stops_count = int(np.floor((distance - fuel_start) / fuel_interval) + 1)
else:
    stops_count = 0

final_energy = initial_energy + stops_count * fuel_kcal - total_calories_burned

# ===============================
# Display Results
# ===============================
st.subheader("Results")
st.write(f"**Race Distance:** {distance:.1f} km")
st.write(f"**Runner Weight:** {weight:.1f} kg")
st.write(f"**Speed:** {speed:.1f} km/h")
st.write(f"**Estimated Race Time:** {formatted_time}")
st.write(f"**Initial Energy Reserve:** {initial_energy:.0f} kcal")
st.write(f"**Total Energy Expenditure:** {total_calories_burned:.0f} kcal")
st.write(f"**Final Energy Reserve:** {final_energy:.0f} kcal")
if fueling_points.size > 0:
    fueling_stops_text = ", ".join([f"{fp:.1f} km" for fp in fueling_points])
    st.write(f"**Fueling Stops at:** {fueling_stops_text}")
    st.write(
        f"**Total Fuel Added:** {stops_count * fuel_kcal:.0f} kcal (from {stops_count} stops)"
    )
else:
    st.write("No fueling stops planned based on the provided strategy.")

# ===============================
# Plot: Energy Reserve vs. Distance
# ===============================
st.subheader("Energy Reserve vs. Distance")
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(
    d_points,
    energy_points,
    "-",
    color="green",
    linewidth=2,
    label="Energy Reserve (kcal)",
)
if fueling_points.size > 0:
    stops_energy = (
        initial_energy
        + (np.floor((fueling_points - fuel_start) / fuel_interval) + 1) * fuel_kcal
        - weight * fueling_points
    )
    ax.scatter(
        fueling_points,
        stops_energy,
        color="blue",
        marker="o",
        s=100,
        label="Fueling Stops",
    )
ax.axhline(0, color="red", linestyle=":", label="Zero Energy Threshold")
ax.set_xlabel("Distance (km)")
ax.set_ylabel("Energy Reserve (kcal)")
ax.set_title("Energy Reserve vs. Distance")
ax.legend(loc="upper right")
ax.grid(True)
plt.tight_layout()
st.pyplot(fig)

# ===============================
# Strategy Analysis
# ===============================
st.subheader("Strategy Analysis")
st.markdown(
    f"""
**Summary:**

- **Glycogen Energy Estimate:**  
  The model assumes ~24 kcal/kg from muscle glycogen plus ~400 kcal from liver stores. For a 70 kg athlete, this is about 1,680 kcal + 400 kcal. These values are useful approximations but may vary with training, diet, and muscle mass.

- **Energy Expenditure:**  
  The model uses ~1 kcal per kg per km—a common starting point for planning—but actual costs depend on running economy, terrain, pace, and individual biomechanics.

- **Fueling Strategy:**  
  Starting fueling at {fuel_start:.1f} km and then every {fuel_interval:.1f} km (each stop adding {fuel_kcal:.0f} kcal) is a simplified method to “top‐up” energy during a race. In practice, fueling timing and carbohydrate types may be adjusted based on individual tolerance, pace, and environmental factors. Research (Thomas et al., 2016; Jeukendrup, 2011) supports planned carbohydrate ingestion during prolonged exercise to delay fatigue.

**Overall:**
This model is based on widely used approximations in sports nutrition. It provides a practical starting point for planning your fueling strategy during training and racing. However, keep in mind that these numbers are “ball‐park” figures; individual variations mean you should adjust your plan based on your personal responses during training.
"""
)
