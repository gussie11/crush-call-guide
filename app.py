import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="CRUSH Engagement Guide", page_icon="🗣️", layout="wide")

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
You are an elite Sales Coach using the "CRUSH" methodology.
Your goal is to write a **Narrative Playbook** for an upcoming progression meeting.

**CONTEXT:**
- This is NOT a cold call. The door is open.
- You must speak in natural, fluid paragraphs.

**INPUTS:**
- Customer: {customer_name} ({industry})
- Current Stage: {cdm_stage}
- Product Context: {context}
- User Notes/News: "{user_news}"

**INSTRUCTION ON RESEARCH:**
1. Check User Notes first.
2. If available, Search Google for recent news (last 6 months) about **{customer_name}**.
3. Use this news to build the "Proximity" bridge in Phase 2.

**OUTPUT FORMAT (Follow the 5 Canonical Phases):**

## Phase 1: Preparation (Cognitive Scaffold)
*Write 2 paragraphs on the "Mindset" for this specific deal.*
- Focus on the "Parallel Paths": Distinguish the Company's Logical Goal from the Person's Emotional Fear (Adoption Risk).
- Define exactly what "Change" means for them (e.g., Transactional -> Consultative).

---

## The Talk Track (Execution)

### Phase 2: Opening (The Trust Gateway)
*Explain why we must regulate the room before pitching.*
**The Script:**
> Write the opening. Start with the News/Context to establish Proximity, then pivot to a **Visual Agenda** (Past -> Future -> Path) to lower cognitive load.

### Phase 3: Change (The UCP)
*We must validate the shift they are trying to make.*
**The Script:**
> Write the question to define the **Unique Change Point (UCP)**. 
> "It sounds like you are trying to shift from [Current State] to [Future State]..."
> Ask a validation question to confirm they see the risk in staying the same.

### Phase 4: Solution (Sense-Making)
*Focus on Usage and Support to reduce indecision.*
**The Script:**
> Don't pitch features. Pitch the "Safety" of the solution.
> Write a question about **Usage** (Day 1 experience) or **Support** (Resources) to prove we won't leave them stranded.

### Phase 5: Closing (Harmonization)
*Risk Removal, not pressure.*
**The Script:**
> Ask the **Harmonization Question**: "Why might this NOT work inside {customer_name}?" (Surface blockers/dependencies).
> End with **Risk Reversal**: "What do you need from us to feel safe moving to the next step?"
"""

# --- UI LAYOUT ---
st.title("🗣️ CRUSH Engagement Guide")
st.markdown("Generates a **narrative script** based on the 5-Phase Canonical Architecture.")

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
            
            st.markdown(f"### 🗣️ Engagement Strategy: {customer_name}")
            st.markdown(result_text)
            st.text_area("Copy Raw Text", value=result_text, height=100)
