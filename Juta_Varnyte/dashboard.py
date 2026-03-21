import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import glob
from windrose import WindroseAxes

st.set_page_config(layout="wide")

st.title("Wind Resource & Energy Dashboard")

# ---------------------------------------------------------
# CONTROLS (TOP)
# ---------------------------------------------------------

turbines = {
    "Vestas V164 8MW": {"rated_power":8000,"cut_in":3,"rated_speed":12,"cut_out":25,"rotor_diameter":164},
    "Vestas V150 6MW": {"rated_power":6000,"cut_in":3,"rated_speed":11.5,"cut_out":25,"rotor_diameter":150},
    "Siemens SG 6.0-154": {"rated_power":6000,"cut_in":3,"rated_speed":12,"cut_out":25,"rotor_diameter":154},
    "Nordex N149 5MW": {"rated_power":5000,"cut_in":3,"rated_speed":11.5,"cut_out":25,"rotor_diameter":149},
    "GE Haliade-X 12MW": {"rated_power":12000,"cut_in":3,"rated_speed":11,"cut_out":25,"rotor_diameter":220}
}

heights = [98,123,148,173,198,218,248]

c1, c2 = st.columns(2)

with c1:
    turbine_name = st.selectbox("Choose a wind turbine model:", list(turbines.keys()))

with c2:
    height = st.selectbox("Choose measurement height (m):", heights)

turbine = turbines[turbine_name]
rotor_diameter = turbine["rotor_diameter"]

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

files = glob.glob("*.csv")
df_list = []

for file in files:
    df_temp = pd.read_csv(file, low_memory=False)
    df_list.append(df_temp)

df = pd.concat(df_list, ignore_index=True)

df = df.rename(columns={"Time and Date": "time"})
df["time"] = pd.to_datetime(df["time"], dayfirst=True, errors="coerce")
df = df.dropna(subset=["time"])

df = df.sort_values("time")
df = df.drop_duplicates(subset="time")

df = df.set_index("time")
df = df.resample("10T").mean()
df = df.reset_index()

# ---------------------------------------------------------
# SELECT HEIGHT
# ---------------------------------------------------------

wind_column = f"Horizontal Wind Speed (m/s) at {height}m"
direction_column = f"Wind Direction (deg) at {height}m"

df["wind"] = pd.to_numeric(df[wind_column], errors="coerce")
df["direction"] = pd.to_numeric(df[direction_column], errors="coerce")

df = df.dropna(subset=["wind","direction"])

df.loc[df["wind"] > 100, "wind"] = None
df = df.dropna(subset=["wind"])

# ---------------------------------------------------------
# TIME FILTER
# ---------------------------------------------------------

st.sidebar.header("Filter Data")

min_date = df["time"].min()
max_date = df["time"].max()

start_date, end_date = st.sidebar.date_input(
    "Select time range:",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Apply filter
df = df[(df["time"] >= pd.to_datetime(start_date)) & 
        (df["time"] <= pd.to_datetime(end_date))]

# ---------------------------------------------------------
# CALCULATIONS
# ---------------------------------------------------------

avg_wind = df["wind"].mean()
max_wind = df["wind"].max()

def turbine_power(v, turbine):
    if v < turbine["cut_in"]:
        return 0
    elif v < turbine["rated_speed"]:
        return turbine["rated_power"] * ((v - turbine["cut_in"]) / (turbine["rated_speed"] - turbine["cut_in"]))**3
    elif v < turbine["cut_out"]:
        return turbine["rated_power"]
    else:
        return 0

def wake_loss_factor(spacing_d):
    if spacing_d < 4:
        return 0.20
    elif spacing_d < 6:
        return 0.12
    elif spacing_d < 8:
        return 0.08
    elif spacing_d < 10:
        return 0.05
    else:
        return 0.03

df["power_kw"] = df["wind"].apply(lambda v: turbine_power(v, turbine))

time_hours = 10 / 60
df["energy_kwh"] = df["power_kw"] * time_hours

total_energy = df["energy_kwh"].sum() / 1000

hours_measured = len(df) * time_hours
annual_energy = total_energy * (8760 / hours_measured)

capacity_factor = df["energy_kwh"].sum() / (turbine["rated_power"] * hours_measured)

df["year_month"] = df["time"].dt.to_period("M")

monthly_avg = df.groupby("year_month")["wind"].mean()
monthly_energy = df.groupby("year_month")["energy_kwh"].sum() / 1000


# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Overview",
    "Monthly Analysis",
    "Wind Distribution",
    "Turbine Direction",
    "Turbine Performance",
    "Wind Farm Design",
    "Financial Analysis"
])

# ---------------------------------------------------------
# TAB 1: OVERVIEW
# ---------------------------------------------------------

with tab1:

    col1, col2 = st.columns([1,2])

    # LEFT SIDE → TEXT + METRICS
    with col1:
        st.subheader("Overview")

        st.write("""
        This section provides a general summary of the wind resource 
        at the selected height and its suitability for energy production.
        
        Key metrics include average wind speed, extreme values, 
        and estimated energy output using the selected turbine model.
        """)

        st.markdown("### Key Results")

        st.write(f"• Average wind speed: **{avg_wind:.2f} m/s**")
        st.write(f"• Maximum wind speed: **{max_wind:.2f} m/s**")
        st.write(f"• Energy (measured): **{total_energy:.0f} MWh**")
        st.write(f"• Estimated annual: **{annual_energy:.0f} MWh**")
        st.write(f"• Capacity factor: **{capacity_factor*100:.1f}%**")

        st.markdown("""
        **Interpretation:**
        - >9 m/s → Excellent offshore wind resource  
        - Capacity factor >40% → Very strong project potential  
        """)

    # RIGHT SIDE → GRAPH
    with col2:
        fig, ax = plt.subplots(figsize=(6,3))
        ax.plot(df["time"], df["wind"])

        ax.set_title(f"Wind Speed at {height} m")
        ax.set_xlabel("Time")
        ax.set_ylabel("Wind Speed (m/s)")

        st.pyplot(fig)

 # ---------------------------------------------------------
# TAB 2: MONTHLY ANALYSIS
# ---------------------------------------------------------

with tab2:

    col1, col2 = st.columns([1,2])

    with col1:
        st.subheader("Monthly Analysis")

        st.write("""
        This section shows how wind conditions and energy production 
        vary throughout the year.

        Seasonal variation is critical for estimating revenue stability 
        and grid integration.
        """)

        st.markdown("### Monthly Energy (MWh)")

        for month, value in monthly_energy.items():
            st.write(f"• {month}: **{value:.0f} MWh**")

        st.markdown("""
        **Interpretation:**
        - Higher winter production is expected offshore  
        - Large variation may impact financial planning  
        """)

    with col2:
        fig, ax = plt.subplots(figsize=(6,3))

        monthly_energy.plot(kind="bar", ax=ax)

        ax.set_title("Monthly Energy Production")
        ax.set_xlabel("Month")
        ax.set_ylabel("Energy (MWh)")

        plt.xticks(rotation=45)

        st.pyplot(fig)

# ---------------------------------------------------------
# TAB 3: WIND DISTRIBUTION
# ---------------------------------------------------------

with tab3:

    col1, col2 = st.columns([1,2])

    with col1:
        st.subheader("Wind Speed Distribution")

        st.write("""
        This histogram shows how frequently different wind speeds occur.

        It is critical because turbine power output depends strongly 
        on wind speed distribution, not just averages.
        """)

        st.markdown(f"""
        **Key Insight:**
        - Most frequent wind speeds define energy production
        - Speeds near rated speed (~{turbine['rated_speed']} m/s) are ideal
        """)

    with col2:
        fig, ax = plt.subplots(figsize=(6,3))

        ax.hist(df["wind"], bins=30, density=True)

        ax.set_title("Wind Speed Distribution")
        ax.set_xlabel("Wind Speed (m/s)")
        ax.set_ylabel("Probability")

        st.pyplot(fig)

# ---------------------------------------------------------
# TAB 4: WIND ROSE
# ---------------------------------------------------------

with tab4:

    col1, col2 = st.columns([1,2])

    with col1:
        st.subheader("Wind Direction Analysis")

        st.write("""
        The wind rose shows how wind speed and direction are distributed.

        It is essential for turbine layout and orientation in a wind farm.
        """)

        # Find dominant direction
        dominant_dir = df["direction"].mean()

        st.markdown(f"""
        **Key Insight:**
        - Dominant wind direction: **~{dominant_dir:.0f}°**
        - Turbines should face this direction for maximum efficiency
        """)

        st.markdown("""
        **How to read:**
        - Each “arm” = wind direction  
        - Length = frequency  
        - Colors = wind speed ranges  
        """)
    
    with col2:
        fig = plt.figure(figsize=(3.5,3.5))  # ✅ smaller figure

        ax = WindroseAxes.from_ax(fig=fig)

        ax.bar(
            df["direction"],
            df["wind"],
            bins=[0,4,8,12,16,20,25],
        normed=True,
        opening=0.8,
            edgecolor='white'
        )

        ax.set_title("Wind Rose", fontsize=10)

    
        ax.set_legend(
            title="m/s",
            fontsize=7,
            title_fontsize=8,
            loc="lower left",
            bbox_to_anchor=(1.0, 0)
        )

        st.pyplot(fig)



# ---------------------------------------------------------
# TAB 5: TURBINE PERFORMANCE
# ---------------------------------------------------------

with tab5:

    col1, col2 = st.columns([1,2])

    with col1:
        st.subheader("Turbine Power Curve")

        st.write("""
        The power curve shows how much electricity the turbine produces 
        at different wind speeds.

        It is one of the most important characteristics of a wind turbine.
        """)

        st.markdown(f"""
        **Key points:**
        - Cut-in speed: {turbine['cut_in']} m/s  
        - Rated speed: {turbine['rated_speed']} m/s  
        - Cut-out speed: {turbine['cut_out']} m/s  
        """)

        st.write(f"Rotor diameter: {rotor_diameter} m")

    with col2:
        speeds = list(range(0, 30))
        powers = [turbine_power(v, turbine) for v in speeds]

        fig, ax = plt.subplots(figsize=(5,3))
        ax.plot(speeds, powers)

        ax.set_title("Power Curve")
        ax.set_xlabel("Wind Speed (m/s)")
        ax.set_ylabel("Power (kW)")

        st.pyplot(fig)

# ---------------------------------------------------------
# TAB 6: WIND FARM DESIGN
# ---------------------------------------------------------

with tab6:

    col1, col2 = st.columns([1,2])

    # ---------------- LEFT: INPUTS ----------------
    with col1:
        st.subheader("Wind Farm Layout")

        num_turbines = st.slider("Number of turbines", 1, 200, 50)

        spacing_downwind = st.slider(
            "Downwind spacing (rotor diameters, D)",
            3.0, 12.0, 7.0
        )

        spacing_crosswind = st.slider(
            "Crosswind spacing (rotor diameters, D)",
            3.0, 12.0, 5.0
        )

        spacing_downwind_m = spacing_downwind * rotor_diameter
        spacing_crosswind_m = spacing_crosswind * rotor_diameter

        st.markdown("### Spacing (meters)")
        st.write(f"• Downwind: {spacing_downwind_m:.0f} m")
        st.write(f"• Crosswind: {spacing_crosswind_m:.0f} m")

    # Wake model
    def wake_loss_factor(spacing_d):
        if spacing_d < 4:
            return 0.20
        elif spacing_d < 6:
            return 0.12
        elif spacing_d < 8:
            return 0.08
        elif spacing_d < 10:
            return 0.05
        else:
            return 0.03

    # Use downwind spacing (more important physically)
    wake_loss = wake_loss_factor(spacing_downwind)

    st.markdown("### Wake Effects")
    st.write(f"• Estimated wake loss: {wake_loss*100:.1f}%")

    # Save for other tabs
    st.session_state["num_turbines"] = num_turbines
    st.session_state["wake_loss"] = wake_loss
    st.session_state["spacing_downwind"] = spacing_downwind
    st.session_state["spacing_crosswind"] = spacing_crosswind

    # -------------- LAYOUT VISUAL ----------------
    with col2:
        import numpy as np


        # Dominant wind direction (already computed earlier)
        wind_dir = df["direction"].mean()

        # Convert to radians
        theta = np.radians(wind_dir)

        # Grid layout
        cols = int(np.sqrt(num_turbines))
        rows = int(np.ceil(num_turbines / cols))

        x = []
        y = []

        for i in range(rows):
            for j in range(cols):
                if len(x) < num_turbines:
                    x.append(j * spacing_crosswind_m)
                    y.append(i * spacing_downwind_m)

        x = np.array(x)
        y = np.array(y)

        # Rotate layout based on wind direction
        x_rot = x * np.cos(theta) - y * np.sin(theta)
        y_rot = x * np.sin(theta) + y * np.cos(theta)

        # Create plot
        fig, ax = plt.subplots(figsize=(6,6))

        # Plot turbines
        ax.scatter(x_rot, y_rot)

        # Add arrows showing wind direction
        arrow_length = rotor_diameter * 2

        for xi, yi in zip(x_rot, y_rot):
            ax.arrow(
                xi, yi,
                arrow_length * np.sin(theta),
                arrow_length * np.cos(theta),
                head_width=rotor_diameter * 0.3,
                length_includes_head=True
            )

        # Add cardinal directions
        ax.text(0, arrow_length*3, "N", ha='center')
        ax.text(arrow_length*3, 0, "E", va='center')
        ax.text(0, -arrow_length*3, "S", ha='center')
        ax.text(-arrow_length*3, 0, "W", va='center')

        # Labels
        ax.set_title("Wind Farm Layout & Orientation")
        ax.set_xlabel("Distance (m)")
        ax.set_ylabel("Distance (m)")

        ax.set_aspect('equal')


        # Draw spacing example (first two turbines)
        if len(x_rot) > 1:
            ax.plot(
                [x_rot[0], x_rot[1]],
                [y_rot[0], y_rot[1]]
            )

            mid_x = (x_rot[0] + x_rot[1]) / 2
            mid_y = (y_rot[0] + y_rot[1]) / 2

            ax.text(mid_x, mid_y, f"{spacing_crosswind_m:.0f} m")

        st.pyplot(fig)

# ---------------------------------------------------------
# TAB 7: FINANCIAL ANALYSIS
# ---------------------------------------------------------

with tab7:

    col1, col2 = st.columns([1,2])

    # ---------------- INPUTS ----------------
    with col1:
        st.subheader("Financial Parameters")

        electricity_price = st.number_input(
            "Electricity price (€/MWh)", value=80.0
        )

        capex = st.number_input(
            "CAPEX (€/MW installed)", value=3000000.0
        )

        opex = st.number_input(
            "OPEX (% of CAPEX per year)", value=3.0
        )

        lifetime = st.slider(
            "Project lifetime (years)", 10, 30, 25
        )

        discount_rate = st.slider(
            "Discount rate (%)", 1.0, 15.0, 7.0
        ) / 100

        st.markdown("---")

        # Pull values from Wind Farm Design tab
        num_turbines = st.session_state.get("num_turbines", 1)
        wake_loss = st.session_state.get("wake_loss", 0.1)

        spacing_along = st.session_state.get("spacing_downwind", 7)
        spacing_cross = st.session_state.get("spacing_crosswind", 5)


    # ---------------- CALCULATIONS ----------------
    adjusted_energy = annual_energy * (1 - wake_loss)
    total_energy_farm = adjusted_energy * num_turbines

    installed_capacity_mw = (turbine["rated_power"] / 1000) * num_turbines

    total_capex = capex * installed_capacity_mw
    annual_revenue = total_energy_farm * electricity_price
    annual_opex = total_capex * (opex / 100)

    annual_profit = annual_revenue - annual_opex

    # NPV
    npv = -total_capex
    for year in range(1, lifetime + 1):
        npv += annual_profit / ((1 + discount_rate) ** year)

    # Payback period
    cumulative = 0
    payback = None
    for year in range(1, lifetime + 1):
        cumulative += annual_profit
        if cumulative >= total_capex and payback is None:
            payback = year

    # ---------------- RESULTS ----------------
    with col2:
        st.subheader("Financial Results")

        st.write(f"• Total CAPEX: **{total_capex:,.0f} €**")
        st.write(f"• Annual revenue: **{annual_revenue:,.0f} €**")
        st.write(f"• Annual OPEX: **{annual_opex:,.0f} €**")
        st.write(f"• Annual profit: **{annual_profit:,.0f} €**")

        st.markdown("### Key Metrics")

        st.write(f"• NPV: **{npv:,.0f} €**")

        if payback:
            st.write(f"• Payback period: **{payback} years**")
        else:
            st.write("• Payback period: Not reached")

        st.markdown("""
        **Interpretation:**
        - Positive NPV → project is profitable  
        - Payback < 15 years → strong investment  
        """)

    # ---------------- EXPLANATION ----------------
    st.markdown("---")

    with st.expander("INFO - Financial Terms Explained"):
        st.markdown("""
        **NPV (Net Present Value)**  
        Total value of the project over its lifetime, accounting for time and risk.  
        → Positive = good investment

        **Discount rate**  
        Reflects risk and the fact that money today is worth more than future money

        **CAPEX**  
        Initial cost to build the wind farm

        **OPEX**  
        Yearly cost of maintenance and operation

        **Payback period**  
        Time needed to recover the initial investment
        """)
