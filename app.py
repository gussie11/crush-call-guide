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

# --- MODEL CONFIGURATION ---
MODEL_NAME = 'models/gemini-2.0-flash-exp'

# --- GENERATION LOGIC ---
def generate_call_guide(prompt, use_search=True):
    # ATTEMPT 1: Search Mode
    if use_search:
        try:
            model = genai.GenerativeModel(MODEL_NAME, tools='google_search_retrieval')
            response = model.generate_content(prompt)
            return response.text, True
        except Exception:
            pass 
            
    # ATTEMPT 2: Fallback
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text, False
    except Exception as e:
        return f"Critical Error: {str(e)}", False

# --- PROMPT LOGIC ---
MASTER_PROMPT = """
You are an expert Sales Coach using the "CRUSH" methodology. 
Your task is to write a **Rep-Facing Call Guide** for a specific sales conversation.

**INSTRUCTION ON RESEARCH:**
1. Check **User Provided News** below.
2. If available, Search Google for **recent news** (last 6 months) about **{customer_name}**.
3. Fallback to internal knowledge if needed.

**USER PROVIDED NEWS / CONTEXT:**
"{user_news}"

**THE GOLDEN RULES:**
1. This is NOT a pitch. Do not list features.
2. This is a decision-alignment conversation.
3. You must follow the exact 3-part cadence: Frame -> Shape -> Remove Fear.

**INPUTS:**
- Customer: {customer_name} ({industry})
- Role: {rubie_role}
- Stage: {cdm_stage}
- Context: {context}

**LOGIC FOR THIS STAKEHOLDER ({rubie_role}):**
{role_logic}

**OUTPUT FORMAT (Markdown):**

## 🎯 Context Briefing (Read First)
*Summarize the key News or Industry Trends here as 3-4 distinct bullet points. Do not script this part; just list the facts.*
* **News/Trend:** ...
* **Strategic implication:** ...

---

## 1. Frame the Decision (The Opening)
*Goal: Clarify why we are here and confirm the decision stage.*
- **Context Hook:** Provide a natural, short opening line referencing the context above (e.g., "I saw the news about X...").
- **Stage Check:** Question to confirm they are at **{cdm_stage}**.
- **Role Check:** Question to confirm their role as **{rubie_role}**.

## 2. Shape the Future (The Middle)
*Goal: Define specific adoption outcomes and risk.*
*CRUSH Focus Areas:* **{focus_areas}**
- **Change:** Question defining where they are today vs. future state.
- **{focus_topic_1}:** 2 High-impact questions.
- **{focus_topic_2}:** 2 High-impact questions.
- *Remind the rep: "If Change is unclear, stop."*

## 3. Remove Fear (Harmonization)
*Goal: Surface blockers.*
- **Harmonization Questions:** 3 specific questions to uncover friction/dependencies (Use the Context Briefing to predict these blockers).
- **Close:** Exact script for "Consolidate Clarity".
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
st.markdown("Generates a call script using **Hybrid Research** (Google Search + Your Notes).")

with st.form("call_form"):
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("Customer Company Name", placeholder="e.g. Acme Corp")
        industry = st.text_input("Industry / Vertical", placeholder="e.g. Manufacturing")
    with col2:
        context = st.text_input("Product/Context", placeholder="e.g. ERP Migration")
        rubie_role = st.selectbox("RUBIE Perspective", list(ROLE_LOGIC_MAP.keys()))

    col3, col4 = st.columns(2)
    with col3:
