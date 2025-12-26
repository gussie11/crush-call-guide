import streamlit as st
import pandas as pd
import plotly.express as px

st.title("🎯 CRUSH Proximity Calculator")

# --- 1. DEFINE THE SCORING LOGIC ---
# This would ideally come from your "CRUSH - Proximity" document
def calculate_proximity(raid_role, rubie_view):
    # Power (Who can sign?)
    power_map = {
        "Decide": 10, "Agree": 8, "Recommend": 6, "Input": 3, "None": 0
    }
    
    # Pain/Impact (Who feels it?)
    # RUBIE logic: Users feel it most; Ripples feel side effects; Buyers feel cost.
    impact_map = {
        "USER (Direct Usage)": 10,
        "BENEFACTOR (Outcome Owner)": 9,
        "IMPLEMENTOR (Deployment)": 7,
        "RIPPLE (Indirectly Affected)": 5,
        "ECONOMIC BUYER (Budget)": 4, # Often distant from the actual problem
        "None": 0
    }
    
    return power_map.get(raid_role, 0), impact_map.get(rubie_view, 0)

# --- 2. INPUT FORM ---
with st.sidebar.form("stakeholder_form"):
    name = st.text_input("Stakeholder Name")
    raid = st.selectbox("RAID Role", ["Decide", "Agree", "Recommend", "Input", "None"])
    rubie = st.selectbox("RUBIE View", ["USER (Direct Usage)", "BENEFACTOR (Outcome Owner)", "IMPLEMENTOR (Deployment)", "RIPPLE (Indirectly Affected)", "ECONOMIC BUYER (Budget)"])
    submitted = st.form_submit_button("Add Stakeholder")

    if submitted:
        # Save to session state list
        power, impact = calculate_proximity(raid, rubie)
        st.session_state.stakeholders.append({
            "Name": name, 
            "Power": power, 
            "Impact": impact, 
            "Role": f"{raid} / {rubie}"
        })

# --- 3. VISUALIZE ---
if st.session_state.stakeholders:
    df = pd.DataFrame(st.session_state.stakeholders)
    
    # Create the Bullseye Chart
    fig = px.scatter(df, x="Impact", y="Power", text="Name", 
                     title="Stakeholder Proximity Map",
                     range_x=[0, 11], range_y=[0, 11],
                     size_max=60)
    
    # Add quadrants/zones
    fig.add_shape(type="circle", xref="x", yref="y", x0=3, y0=3, x1=7, y1=7, line_color="green")
    
    st.plotly_chart(fig)
    
    st.write("### Analysis")
    st.write("- **Top Right (High Power/High Impact):** These are your Mobilizers. Focus here.")
    st.write("- **Top Left (High Power/Low Impact):** Dangerous. They decide but don't care. You must bridge the gap.")
