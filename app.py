import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="CRUSH Engagement Guide", page_icon="🧠", layout="wide")

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
# Using the experimental model as it works for your key
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
Your task is to write a **Sales Engagement Guide** based on the Canonical Architecture.

**INSTRUCTION ON RESEARCH:**
1. Check **User Provided News** below.
2. If available, Search Google for **recent news** (last 6 months) about **{customer_name}**.
3. Use the news to inform the "Proximity Hook" and "Harmonization" sections.

**THEORETICAL BASIS (CANONICAL):**
- [cite_start]**Parallel Paths:** Track Company Goals vs. People Fears[cite: 184].
- [cite_start]**Neuroscience:** Low proximity triggers cortisol (defense); high proximity triggers oxytocin (trust)[cite: 204].
- [cite_start]**Adoption Risk:** The primary barrier is not "lack of pain" but "fear of the future"[cite: 179].

**INPUTS:**
- Customer: {customer_name} ({industry})
- Role: {rubie_role}
- Stage: {cdm_stage}
- Context: {context}
- User Notes: "{user_news}"

**LOGIC FOR THIS STAKEHOLDER ({rubie_role}):**
{role_logic}

**OUTPUT FORMAT (Markdown):**

## 🧠 Phase 1: Pre-Call Preparation (Cognitive Scaffold)
*Internal Strategy Only. Do not read to customer.*
* **Company Path (Logic):** Identify 1 strategic goal and 1 business risk for {customer_name}.
* **People Path (Emotion):** Identify the specific Aspiration and Fear for a **{rubie_role}** in this situation.

---

## 📞 Rep-Facing Engagement Script

### Phase 2: Opening (Trust Gateway)
*Goal: Regulate neurochemistry. Set a collaborative frame.*
- **Proximity Hook:** Write a natural opening line referencing the News/Context found.
- **Visual Agenda:** Script the transition to a "Visual Agenda" (Past -> Future -> Path) to lower cognitive load.
- **Check:** "Does that map to where you are?"

### Phase 3: Change (The UCP)
*Goal: Shift from Pain to Adoption Risk.*
- **Unique Change Point (UCP):** Ask a question that contrasts their Current State vs. Future State.
- **RUBIE Validation:** Ask 2 questions specific to **{rubie_role}** concerns ({focus_areas}) to validate their view of success.

### Phase 4: Solution (Sense-Making)
*Goal: Orchestrate Sense-Making.*
- **Usage & Support:** Ask a question about "Day 1" (Usage) or "Implementation" (Support) to reduce fear of the future state.
- **Recommendation:** "Based on this, I recommend we..." (Limit choices).

### Phase 5: Closing (Harmonization)
*Goal: Risk Removal.*
- **Blocker Identification:** "Why might this NOT work here?" (Surface dependencies/friction).
- **Risk Reversal:** "What do you need from us to feel safe moving to the next step?"
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
st.title("🧠 CRUSH Engagement Guide")
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
                user_news=user_news if user_news else "None provided.",
                role_logic=role_data['logic'],
                focus_areas=role_data['focus_areas']
            )
            
            result_text, search_success = generate_call_guide(final_prompt, use_search=use_search)
            
            if use_search and not search_success:
                st.info("ℹ️ **Note:** Auto-Search unavailable. Using your notes & internal knowledge.")
            elif use_search and search_success:
                st.success("✅ Live Research Complete.")
            
            st.markdown(f"### 🧠 Engagement Strategy for {customer_name}")
            st.markdown(result_text)
            st.text_area("Copy Raw Text", value=result_text, height=100)
