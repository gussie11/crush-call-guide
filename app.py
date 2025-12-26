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
.warning-box {
    padding: 1rem;
    background-color: #fff3cd;
    border-radius: 8px;
    border-left: 5px solid #ffc107;
    margin-bottom: 1rem;
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
MODEL_NAME = 'models/gemini-1.5-flash'

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
Your task is to write a **Strategic Prep Brief** and **Rep-Facing Call Guide**.

**INSTRUCTION ON RESEARCH:**
1. Check **User Provided News** below.
2. If available, Search Google for **recent news** (last 6 months) about **{customer_name}** in **{industry}**.
3. Fallback to internal knowledge if needed.

**USER PROVIDED NEWS / CONTEXT:**
"{user_news}"

**THEORY: HOLISTIC SELLING & PARALLEL PATHS**
- **Company Path:** Logic, Goals, Risks (CDM Journey).
- **People Path:** Emotion, Aspirations, Fears (RUBIE Perspective).
- **Neuro-Rule:** You cannot solve a "Person" fear with a "Company" goal.

**INPUTS:**
- Customer: {customer_name} ({industry})
- Role: {rubie_role}
- Stage: {cdm_stage}
- Context: {context}
- **Proximity Level:** {proximity} (See specific instructions below)

**LOGIC FOR THIS STAKEHOLDER ({rubie_role}):**
{role_logic}

**OUTPUT FORMAT (Markdown):**

## 🧠 Phase 0: Pre-Call Strategy (Internal Prep)
*Do not read this to the customer. This is your cognitive scaffold.*

### 1. Proximity Assessment
* **Current Level:** {proximity}
* **Neuro-Impact:** *(If Level 4: "Warning: Low trust. High Cortisol risk. Strategy: Pivot to Level 3 via industry relevance." | If Level 1-2: "High Trust. Use Oxytocin pathway.")*

### 2. The Parallel Paths (Holistic Map)
* **🏢 Company Path (Logic):**
    * *Goal:* [Predict 1 strategic goal based on Industry/Stage]
    * *Risk:* [Predict 1 business risk]
* **👤 People Path (Emotion):**
    * *Aspiration:* [Predict what this {rubie_role} wants personally, e.g., promotion, ease]
    * *Fear:* [Predict their specific Adoption Risk, e.g., "looking foolish"]

---

## 🎯 Context Briefing
* **News/Trend:** ...
* **Strategic implication:** ...

---

## 📞 Rep-Facing Call Script

### 1. Frame the Decision (The Opening)
*Goal: Regulate neurochemistry (Safety) and confirm Stage.*
- **Context Hook:** "I saw the news about..." (Use Level 3 Related Proximity).
- **Stage Check:** Question to confirm **{cdm_stage}**.
- **Role Check:** Question to confirm **{rubie_role}**.

### 2. Shape the Future (The Middle)
*Goal: Reduce Cognitive Load. Define Change.*
*CRUSH Focus Areas:* **{focus_areas}**
- **Change:** Question defining "Where are you today?" vs. "Future State".
- **{focus_topic_1}:** 2 High-impact questions mapping to the **People Path**.
- **{focus_topic_2}:** 2 High-impact questions mapping to the **Company Path**.

### 3. Remove Fear (Harmonization)
*Goal: Address Adoption Risk.*
- **Harmonization:** 3 questions to uncover "Why might this NOT work?" (Blockers/Dependencies).
- **Close:** Exact script for "Consolidate Clarity" (Not "Closing").
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
st.markdown("Generates a **Holistic Sales Strategy** (Prep + Script) using Hybrid Research.")

with st.form("call_form"):
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("Customer Company Name", placeholder="e.g. Acme Corp")
        industry = st.text_input("Industry / Vertical", placeholder="e.g. Manufacturing")
        rubie_role = st.selectbox("RUBIE Perspective", list(ROLE_LOGIC_MAP.keys()))

    with col2:
        context = st.text_input("Product/Context", placeholder="e.g. ERP Migration")
        cdm_stage = st.selectbox("Current Decision Stage (CDM)", 
                                 ["Stage 0->1 (Mobilizing)", 
                                  "Stage 1 (Sources)", 
                                  "Stage 2 (Selected)", 
                                  "Stage 3 (Ordered)", 
                                  "Stage 4 (Usage)", 
                                  "Stage 7 (Renew)"])
        # NEW PROXIMITY FIELD
        proximity = st.selectbox("Current Proximity Level", 
                                 ["Level 1 (Direct - Insider)", 
                                  "Level 2 (Transferred - Referral)", 
                                  "Level 3 (Related - Industry)", 
                                  "Level 4 (Clichés - Cold)"])

    user_news = st.text_area("Recent News / Context (Optional)", 
                             placeholder="Paste recent news here if Search fails.",
                             height=80)
    
    use_search = st.checkbox("Attempt Google Search (Grounding)", value=True)
    submit = st.form_submit_button("Generate Strategy & Guide")

if submit:
    if not customer_name or not context:
        st.warning("⚠️ Please fill in Customer Name and Product Context.")
    else:
        role_data = ROLE_LOGIC_MAP[rubie_role]
        
        with st.spinner(f"🔍 Analyzing '{customer_name}'..."):
            final_prompt = MASTER_PROMPT.format(
                customer_name=customer_name,
                industry=industry,
                rubie_role=rubie_role,
                cdm_stage=cdm_stage,
                context=context,
                proximity=proximity,
                user_news=user_news if user_news else "None provided.",
                role_logic=role_data['logic'],
                focus_areas=role_data['focus_areas'],
                focus_topic_1=role_data['topics'][0],
                focus_topic_2=role_data['topics'][1] if len(role_data['topics']) > 1 else "Harmonization"
            )
            
            result_text, search_success = generate_call_guide(final_prompt, use_search=use_search)
            
            if use_search and not search_success:
                st.info("ℹ️ **Note:** Auto-Search unavailable. Using your notes & internal knowledge.")
            elif use_search and search_success:
                st.success("✅ Live Research Complete.")
            
            st.markdown(f"### 📝 Strategic Guide for {customer_name}")
            st.markdown(result_text)
            st.text_area("Copy Raw Text", value=result_text, height=100)
