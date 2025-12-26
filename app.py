import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="CRUSH Sales Engagement Guide", page_icon="🧠", layout="wide")

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
# We are sticking to the version that works for your key.
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
            
    # ATTEMPT 2: Fallback (Safe Mode)
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text, False
    except Exception as e:
        return f"Critical Error: {str(e)}", False

# --- PROMPT LOGIC ---
MASTER_PROMPT = """
You are an expert Sales Coach using the "CRUSH" methodology. 
Your task is to write a **Sales Engagement Guide** based strictly on the Canonical Architecture.

**INSTRUCTION ON RESEARCH:**
1. Check **User Provided News** below.
2. If available, Search Google for **recent news** (last 6 months) about **{customer_name}** in **{industry}**.
3. Fallback to internal knowledge if needed.

**USER PROVIDED NEWS / CONTEXT:**
"{user_news}"

**THEORETICAL BASIS (CANONICAL):**
- **Goal:** Regulate threat responses and reduce Adoption Risk[cite: 282].
- **Parallel Paths:** You must track the "Company Path" (Goals/Risks) and "People Path" (Aspirations/Fears) [cite: 250-252].
- **Neuroscience:** Low proximity triggers cortisol (defense); high proximity triggers oxytocin (trust)[cite: 204].

**INPUTS:**
- Customer: {customer_name} ({industry})
- Role: {rubie_role}
- Stage: {cdm_stage}
- Context: {context}
- **Proximity Level:** {proximity} (See specific instructions below)

**LOGIC FOR THIS STAKEHOLDER ({rubie_role}):**
{role_logic}

**OUTPUT FORMAT (Markdown):**

## 🧠 Phase 1: Pre-Call Preparation — Cognitive Scaffold
*Internal Strategy Only. Do not read to customer.* [cite: 249]

### 1. Proximity & Neuro-Assessment
* **Current Level:** {proximity}
* **Strategy:** *(If Level 4: "Warning: Generic claims will trigger cortisol/defense. Pivot to Level 3 via industry context." | If Level 1-2: "Trust exists. Use oxytocin pathway.")* [cite: 204-206]

### 2. The Parallel Paths (Holistic Map) [cite: 184]
* **🏢 Company Path (Logic):**
    * *Goal:* [Predict 1 strategic goal based on Industry/Stage]
    * *Risk:* [Predict 1 business risk]
* **👤 People Path (Emotion):**
    * *Aspiration:* [Predict what this {rubie_role} wants personally]
    * *Fear:* [Predict their specific Adoption Risk, e.g., "looking foolish"]

---

## 🎯 Context Briefing
* **News/Trend:** ...
* **Strategic implication:** ...

---

## 📞 Rep-Facing Engagement Script

### Phase 2: Opening — Trust Gateway [cite: 257]
*Goal: Regulate neurochemistry. Set a collaborative frame.*
- **Proximity Hook:** "I saw the news about..." (Establish Level 2 or 3 Proximity).
- **Visual Agenda Frame:** Script a concise "Visual Agenda" statement that maps: Current State -> Destination -> Path [cite: 259-262].
- **Alignment Check:** "Does that map to where you are?"

### Phase 3: Change [cite: 264]
*Goal: Shift from Pain to Adoption Risk.*
- **Unique Change Point (UCP):** Define the shift they need to make (e.g., Transactional -> Consultative).
- **RUBIE Validation:** Ask 2 questions specific to the **{rubie_role}** perspective to validate their view of success/risk[cite: 268].

### Phase 4: Solution [cite: 269]
*Goal: Orchestrate Sense-Making.*
- **Usage & Support Check:** Ask a question about "Day 1" (Usage) or "Implementation" (Support) to reduce fear of the future state[cite: 272].
- **Recommendation:** "Based on this, I recommend we..." (Limit choices to reduce analysis paralysis)[cite: 273].

### Phase 5: Closing — Harmonization [cite: 274]
*Goal: Risk Removal.*
- **Blocker Identification:** "Why might this NOT work here?" (Surface dependencies/friction) [cite: 124, 276].
- **Risk Reversal:** "What do you need from us to feel safe moving to the next step?"[cite: 278].
"""

# --- LOGIC MAPPING ---
ROLE_LOGIC_MAP = {
    "Economic Buyer (Budget)": {
        "logic": "Focus on ROI, Financial Risk, and Opportunity Cost. Fear: Late-stage objections.",
        "focus_areas": "Change, Results, Harmonization",
        "topics": ["Results (ROI/Outcomes)", "Risk (Financial/Political)"]
    },
    "Benefactor (Outcome Owner)": {
        "logic": "Focus on Outcomes, Performance, and Value Realization. Fear: Perceived failure.",
        "focus_areas": "Change, Results, Harmonization",
        "topics": ["Results (KPIs)", "Impact (Business Value)"]
    },
    "User (Direct Usage)": {
        "logic": "Focus on Usability, Effort, and Day-to-Day Experience. Fear: Workarounds/Abandonment.",
        "focus_areas": "Usage, Support, Harmonization",
        "topics": ["Usage (Day-to-Day)", "Support (Enablement)"]
    },
    "Implementor (Deployment)": {
        "logic": "Focus on Feasibility, Complexity, and Timelines. Fear: Delays/Cost Overruns.",
        "focus_areas": "Support, Harmonization",
        "topics": ["Implementation (Feasibility)", "Support (Resources)"]
    },
    "Ripple (Indirectly Affected)": {
        "logic": "Focus on Downstream Impact and Disruption. Fear: Unintended Consequences.",
        "focus_areas": "Harmonization",
        "topics": ["Disruption (Downstream)", "Dependencies"]
    }
}

# --- UI LAYOUT ---
st.title("🧠 CRUSH Sales Engagement Guide")
st.markdown("Generates a **Neuro-Behavioral Call Strategy** based on the Canonical Architecture.")

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
        # PROXIMITY LEVEL
        proximity = st.selectbox("Current Proximity Level", 
                                 ["Level 1 (Direct - Insider)", 
                                  "Level 2 (Transferred - Referral)", 
                                  "Level 3 (Related - Industry)", 
                                  "Level 4 (Clichés - Cold)"])

    user_news = st.text_area("Recent News / Context (Optional)", 
                             placeholder="Paste recent news here if Search fails.",
                             height=80)
    
    use_search = st.checkbox("Attempt Google Search (Grounding)", value=True)
    submit = st.form_submit_button("Generate Engagement Guide")

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
            )
            
            result_text, search_success = generate_call_guide(final_prompt, use_search=use_search)
            
            if use_search and not search_success:
                st.info("ℹ️ **Note:** Auto-Search unavailable. Using your notes & internal knowledge.")
            elif use_search and search_success:
                st.success("✅ Live Research Complete.")
            
            st.markdown(f"### 🧠 Engagement Strategy for {customer_name}")
            st.markdown(result_text)
            st.text_area("Copy Raw Text", value=result_text, height=100)
