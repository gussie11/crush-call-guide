import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions

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
MODEL_NAME = 'models/gemini-2.0-flash-exp'

# --- GENERATION LOGIC ---
def generate_guide(prompt):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- PROMPT LOGIC ---
MASTER_PROMPT = """
You are an expert Sales Coach using the "CRUSH" methodology.
Your task is to write a **Sales Engagement Guide** based strictly on the Canonical Architecture[cite: 162].

**CORE CRUSH PRINCIPLES:**
1. **Parallel Paths:** You must separate the "Company Path" (Logic/Goals) from the "People Path" (Emotion/Fear)[cite: 184].
2. **Adoption Risk:** The enemy is not competition; it is "Adoption Risk" (fear that the future state won't yield value)[cite: 179].
3. **Visual Agenda:** You must script a "Visual Agenda" to lower cognitive load[cite: 227].
4. **Harmonization:** You do not "close." You "Harmonize" (remove risk)[cite: 275].

**INPUTS:**
- Customer: {customer_name} ({industry})
- Product/Context: {context}
- Stage: {cdm_stage}

**OUTPUT FORMAT (Markdown):**

## 🧠 Phase 1: Pre-Call Preparation (The Parallel Paths)
*Define the dual tracks we must manage [cite: 250-252]:*
* **🏢 Company Path (The Logic):** What is the business trying to achieve? (e.g., Efficiency, Market Share).
* **👤 People Path (The Emotion):** What is the human afraid of? (e.g., Loss of status, Complexity, Looking foolish). *Note: You cannot solve a Person fear with a Company goal.*

---

## 📞 Rep-Facing Engagement Script

### Phase 2: Opening (The Trust Gateway)
*Goal: Regulate neurochemistry and lower cognitive load[cite: 258].*
* **The Visual Agenda Script:** Write a concise script that maps:
    1. **Current State:** "We are here."
    2. **Destination:** "We want to get here."
    3. **Path:** "The steps between."
* **Alignment Check:** "Does this map to how you see it?"

### Phase 3: Change (The UCP)
*Goal: Shift from 'Pain' to 'Adoption Risk'[cite: 265].*
* **Unique Change Point (UCP):** Script a question that challenges their status quo.
    * *Draft:* "Most companies in {industry} try to fix [Problem] by [Standard Approach], but they fail because of [Adoption Risk]. How are you ensuring your team actually adopts this change?"

### Phase 4: Solution (Sense-Making)
*Goal: Sell the safety of the decision, not the features[cite: 270].*
* **Usage & Support:** Script a specific question about "Day 1" or "Support" to prove safety.
    * *Draft:* "The technology is the easy part. The hard part is [Usage Challenge]. How will we support your team on Day 1?"

### Phase 5: Closing (Harmonization)
*Goal: Risk Removal (Not 'Closing')[cite: 274].*
* **The Harmonization Question:** Script a question to surface blockers.
    * *Draft:* "Why might this *not* work inside {customer_name}? Who else needs to be aligned?"
* **Risk Reversal:** "What do you need from us to feel safe moving to the next step?"
"""

# --- UI LAYOUT ---
st.title("🧠 CRUSH Canonical Guide")
st.markdown("Generates a **Neuro-Behavioral Call Strategy** based on the Canonical Architecture.")

with st.form("call_form"):
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("Customer Company Name", placeholder="e.g. Acme Corp")
        industry = st.text_input("Industry / Vertical", placeholder="e.g. Manufacturing")

    with col2:
        context = st.text_input("Product/Context", placeholder="e.g. ERP Migration")
        cdm_stage = st.selectbox("Current Decision Stage (CDM)", 
                                 ["Stage 0->1 (Mobilizing)", 
                                  "Stage 1 (Sources)", 
                                  "Stage 2 (Selected)", 
                                  "Stage 3 (Ordered)", 
                                  "Stage 4 (Usage)", 
                                  "Stage 7 (Renew)"])

    submit = st.form_submit_button("Generate Guide")

if submit:
    if not customer_name or not context:
        st.warning("⚠️ Please fill in Customer Name and Product Context.")
    else:
        with st.spinner(f"Drafting Canonical Guide for '{customer_name}'..."):
            final_prompt = MASTER_PROMPT.format(
                customer_name=customer_name,
                industry=industry,
                cdm_stage=cdm_stage,
                context=context
            )
            
            result_text = generate_guide(final_prompt)
            
            st.markdown(f"### 🧠 Engagement Strategy: {customer_name}")
            st.markdown(result_text)
            st.text_area("Copy Raw Text", value=result_text, height=100)
