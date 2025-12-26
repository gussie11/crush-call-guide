import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="CRUSH Progression Guide", page_icon="🗣️", layout="wide")

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
            
    # ATTEMPT 2: Fallback (Safe Mode)
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text, False
    except Exception as e:
        return f"Critical Error: {str(e)}", False

# --- PROMPT LOGIC ---
MASTER_PROMPT = """
You are an elite Sales Coach executing a "Progression Call" using the CRUSH methodology.
Your goal is to write a **Narrative Playbook** for an upcoming meeting. 

**CONTEXT:**
- This is NOT a cold call. The door is open.
- The goal is not to "pitch" but to orchestrate a decision.
- You must speak in natural, fluid paragraphs.

**INPUTS:**
- Customer: {customer_name} ({industry})
- Current Stage: {cdm_stage}
- Product Context: {context}
- User Notes/News: "{user_news}"

**INSTRUCTION ON RESEARCH:**
1. Check User Notes first.
2. If available, Search Google for recent news (last 6 months) about **{customer_name}** to use as conversational bridges.
3. If no news found, rely on industry trends.

**OUTPUT FORMAT:**

## 1. How to Prepare (The Mindset)
*Write 2 short paragraphs explaining exactly what the rep needs to get straight in their head before they dial.*
- Explain the distinction between the "Company Goal" (Logic) and the "Person's Fear" (Emotion) for this specific deal.
- Define what "Adoption Risk" likely looks like here (e.g., "They are afraid of X...").

---

## 2. The Talk Track (Execution)

### The Opening (Regulating the Room)
*Explain in one sentence why we start with a Visual Agenda instead of pleasantries.*
**The Script:**
> Write the exact opening lines. Start with a reference to the news/context provided, then pivot immediately to a "Visual Agenda" to set the frame. 
> "I saw the news about X... which is actually why I wanted to frame our time today..."

### The Middle (Shaping the Future)
*Explain that we need to pivot from "Features" to "Change".*
**The Script:**
> Write the specific questions to ask to define where they are today vs. where they want to be.
> Provide a "Sense-Making" statement: "It sounds like you are trying to move from [Current State] to [Future State], is that right?"

### The End (Harmonization)
*Explain why we don't "Close" but instead "Harmonize".*
**The Script:**
> Write the specific question to uncover blockers. 
> "Typically, initiatives like this fail because of [Blocker]. Why might this NOT work inside {customer_name}?"
> End with the "Consolidate Clarity" statement: "Based on this, what do you need from us to feel confident moving forward?"
"""

# --- UI LAYOUT ---
st.title("🗣️ CRUSH Progression Guide")
st.markdown("Generates a **narrative script** for navigating a live deal.")

with st.form("call_form"):
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("Customer Company Name", placeholder="e.g. Acme Corp")
        industry = st.text_input("Industry / Vertical", placeholder="e.g. Manufacturing")

    with col2:
        context = st.text_input("Product/Context", placeholder="e.g. ERP Migration")
        cdm_stage = st.selectbox("Current Decision Stage", 
                                 ["Mobilizing (Stage 0->1)", 
                                  "Evaluating Sources (Stage 1)", 
                                  "Selecting (Stage 2)", 
                                  "Finalizing Order (Stage 3)", 
                                  "Expansion/Renewal (Stage 7+)"])

    user_news = st.text_area("Recent News / Context (Optional)", 
                             placeholder="Paste any context here (e.g. 'They just merged', 'New CFO').",
                             height=80)
    
    use_search = st.checkbox("Attempt Google Search (Grounding)", value=True)
    submit = st.form_submit_button("Generate Narrative Guide")

if submit:
    if not customer_name or not context:
        st.warning("⚠️ Please fill in Customer Name and Product Context.")
    else:
        with st.spinner(f"🔍 Drafting narrative for '{customer_name}'..."):
            final_prompt = MASTER_PROMPT.format(
                customer_name=customer_name,
                industry=industry,
                cdm_stage=cdm_stage,
                context=context,
                user_news=user_news if user_news else "None provided.",
            )
            
            result_text, search_success = generate_call_guide(final_prompt, use_search=use_search)
            
            if use_search and not search_success:
                st.info("ℹ️ **Note:** Auto-Search unavailable. Using your notes & internal knowledge.")
            elif use_search and search_success:
                st.success("✅ Live Research Complete.")
            
            st.markdown(f"### 🗣️ Progression Strategy: {customer_name}")
            st.markdown(result_text)
            st.text_area("Copy Raw Text", value=result_text, height=100)
