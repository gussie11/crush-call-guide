import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="CRUSH Sales Call Guide", page_icon="📞", layout="wide")

# --- CSS ---
st.markdown("""
<style>
div.stButton > button {
    width: 100%;
    border-radius: 8px;
    height: 3em;
    background-color: #f0f2f6;
    border: 1px solid #d0d2d6;
}
.header-box {
    padding: 1rem;
    background-color: #e8f0fe;
    border-radius: 8px;
    margin-bottom: 1rem;
    border-left: 5px solid #4285f4;
}
</style>
""", unsafe_allow_html=True)

# --- API SETUP ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = None

if not api_key:
    st.error("⚠️ API Key missing. Please set GEMINI_API_KEY in .streamlit/secrets.toml")
    st.stop()

genai.configure(api_key=api_key)
MODEL_NAME = 'models/gemini-2.0-flash-exp'

# --- RETRY LOGIC ---
def generate_content_with_retry(prompt):
    model = genai.GenerativeModel(MODEL_NAME)
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- PROMPT LOGIC ---
MASTER_PROMPT = """
You are an expert Sales Coach using the "CRUSH" methodology. 
Your task is to write a **Rep-Facing Call Guide** for a specific sales conversation.

**THE GOLDEN RULES:**
1. This is NOT a pitch. Do not list features. Do not "sell".
2. This is a decision-alignment conversation.
3. You must follow the exact 3-part cadence: Frame -> Shape -> Remove Fear.

**INPUTS:**
- Customer Name: {customer_name}
- Industry/Type: {industry}
- Stakeholder Role (RUBIE): {rubie_role}
- Current Decision Stage (CDM): {cdm_stage}
- Product/Context: {context}
- **CRITICAL HEADS UP / NEWS:** "{customer_info}"

**LOGIC FOR THIS STAKEHOLDER ({rubie_role}):**
{role_logic}

**OUTPUT FORMAT (Markdown):**

## 1. Frame the Decision (The Opening)
*Goal: Clarify why we are here and confirm the decision stage.*
- **Context Hook:** Provide an opening line that references the Industry ({industry}) or the "Heads Up" info provided above to show relevance.
- **Stage Check:** Include a specific question to confirm they are actually at **{cdm_stage}**.
- **Role Check:** Include a question to confirm their role/concern as **{rubie_role}**.

## 2. Shape the Future (The Middle)
*Goal: Define specific adoption outcomes and risk.*
*CRUSH Focus Areas for this role:* **{focus_areas}**
- **Change:** Ask questions to define where they are today vs. where they want to be. *incorporate industry trends here if relevant.*
- **{focus_topic_1}:** Ask 2 high-impact questions specific to their role's concern.
- **{focus_topic_2}:** Ask 2 high-impact questions specific to their role's concern.
- *Remind the rep: "If Change is unclear, stop. Nothing else matters."*

## 3. Remove Fear (Harmonization)
*Goal: Surface blockers. Answer: "Why might this NOT work?"*
- Provide 3 specific "Harmonization" questions. *Use the 'Heads Up' info to predict specific blockers (e.g., if there is a merger, ask about integration friction).*
- **Closing Question:** Provide the exact script for the "Consolidate Clarity" close.

"""

# --- LOGIC MAPPING ---
ROLE_LOGIC_MAP = {
    "Economic Buyer (Budget)": {
        "logic": "Focus on Change, Results, Harmonization. They care about ROI and financial risk.",
        "focus_areas": "Change, Results, Harmonization",
        "topics": ["Results (ROI/Outcomes)", "Risk (Financial/Political)"]
    },
    "Benefactor (Outcome Owner)": {
        "logic": "Focus on Change, Results, Harmonization. They care about business outcomes and performance.",
        "focus_areas": "Change, Results, Harmonization",
        "topics": ["Results (KPIs)", "Impact (Business Value)"]
    },
    "User (Direct Usage)": {
        "logic": "Focus on Usage, Support, Harmonization. They care about usability, effort, and day-to-day experience.",
        "focus_areas": "Usage, Support, Harmonization",
        "topics": ["Usage (Day-to-Day)", "Support (Enablement)"]
    },
    "Implementor (Deployment)": {
        "logic": "Focus on Support, Harmonization. They care about feasibility, complexity, and timelines.",
        "focus_areas": "Support, Harmonization",
        "topics": ["Implementation (Feasibility)", "Support (Resources)"]
    },
    "Ripple (Indirectly Affected)": {
        "logic": "Focus strictly on Harmonization. They care about downstream impact and disruption.",
        "focus_areas": "Harmonization",
        "topics": ["Disruption (Downstream)", "Dependencies"]
    }
}

# --- UI LAYOUT ---
st.title("📞 CRUSH Sales Call Guide")
st.markdown("Generates a **decision-alignment script** tailored to the customer context.")

with st.form("call_form"):
    # Row 1: Basic Info
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("Customer/Stakeholder Name", placeholder="e.g. Jane Doe")
        industry = st.text_input("Industry / Company Type", placeholder="e.g. Healthcare / Non-Profit")
    with col2:
        context = st.text_input("Product/Context", placeholder="e.g. Enterprise CRM migration")
        rubie_role = st.selectbox("RUBIE Perspective", list(ROLE_LOGIC_MAP.keys()))

    # Row 2: Stage & Context
    col3, col4 = st.columns(2)
    with col3:
        cdm_stage = st.selectbox("Current Decision Stage (CDM)", 
                                 ["Stage 0->1 (Mobilizing)", 
                                  "Stage 1 (Sources)", 
                                  "Stage 2 (Selected)", 
                                  "Stage 3 (Ordered)", 
                                  "Stage 4 (Usage)", 
                                  "Stage 7 (Renew)"])
    with col4:
        customer_info = st.text_area("Recent News / Heads Up (Optional)", 
                                     placeholder="e.g. New CFO, Merger pending, Budget freeze rumors...",
                                     height=100)
        
    submit = st.form_submit_button("Generate Call Guide")

if submit:
    if not customer_name or not context:
        st.warning("⚠️ Please fill in Customer Name and Product Context.")
    else:
        role_data = ROLE_LOGIC_MAP[rubie_role]
        
        with st.spinner("Drafting Call Guide..."):
            final_prompt = MASTER_PROMPT.format(
                customer_name=customer_name,
                industry=industry,
                rubie_role=rubie_role,
                cdm_stage=cdm_stage,
                context=context,
                customer_info=customer_info if customer_info else "None provided.",
                role_logic=role_data['logic'],
                focus_areas=role_data['focus_areas'],
                focus_topic_1=role_data['topics'][0],
                focus_topic_2=role_data['topics'][1] if len(role_data['topics']) > 1 else "Harmonization"
            )
            
            result = generate_content_with_retry(final_prompt)
            
            st.markdown(f"### 📝 Call Guide for {customer_name}")
            st.markdown(result)
            st.text_area("Copy Raw Text", value=result, height=100)
