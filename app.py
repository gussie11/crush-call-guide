import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="CRUSH Canonical Coach", page_icon="🎓", layout="wide")

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
You are an expert Sales Coach mentoring a rep using the **CRUSH — Sales Engagement (Canonical)** methodology.
Your task is to write a **Coaching Guide** for a specific meeting.

**STRICT SOURCE CONSTRAINT:**
You must ONLY use principles and structures from the "CRUSH — Sales Engagement (Canonical)" document. 
Do not use generic sales advice (e.g., "build rapport", "find pain") unless defined by CRUSH (e.g., "Proximity", "Adoption Risk").

**THE 5 CANONICAL PHASES:**
1. **Pre-Call Preparation:** Parallel Paths (Company vs. People)[cite: 249].
2. **Opening:** Trust Gateway & Visual Agenda[cite: 257].
3. **Change:** Adoption Risk & Unique Change Point (UCP)[cite: 264].
4. **Solution:** Usage & Support (Sense-making)[cite: 269].
5. **Closing:** Harmonization (Risk Removal)[cite: 274].

**INPUTS:**
- Customer: {customer_name} ({industry})
- Product/Context: {context}
- Stage: {cdm_stage}

**OUTPUT FORMAT (Markdown):**

## 🧠 Phase 1: Pre-Call Preparation (Cognitive Scaffold)
**Coach's Context:** "We must track two parallel paths. You cannot solve a 'Person' fear with a 'Company' goal." [cite: 194-195]
* **The Company Path (Logic):** Identify the business goal and risk for {customer_name}.
* **The People Path (Emotion):** Identify the specific *Adoption Risk* (Fear) for the human across the table.

---

## 🗣️ Phase 2: Opening (Trust Gateway)
**Coach's Context:** "Do not rely on pleasantries. Use a Visual Agenda to lower cognitive load and regulate neurochemistry." [cite: 258-259]
* **The Script:** Write the exact opening lines:
    * *Proximity:* Establish connection (Level 2 or 3).
    * *Visual Agenda:* "I’ve mapped out where we are (Current), where you want to go (Destination), and the path between. Does that align?" [cite: 260-263]

## 🗣️ Phase 3: Change
**Coach's Context:** "Shift from 'Pain' to 'Adoption Risk'. Introduce the Unique Change Point (UCP)." [cite: 265-267]
* **The Script:** Write the question to define the shift.
    * *Draft:* "The industry is shifting from [Old Way] to [New Way]. The risk isn't the technology, it's the adoption. How are you viewing that shift?"

## 🗣️ Phase 4: Solution
**Coach's Context:** "Orchestrate sense-making. Address Usage and Support to reduce indecision." [cite: 270-272]
* **The Script:** Don't pitch features. Ask about "Day 1."
    * *Draft:* "To ensure value, we need to solve for [Usage/Support]. How will your team handle [Specific Implementation Challenge]?"

## 🗣️ Phase 5: Closing (Harmonization)
**Coach's Context:** "Do not 'close'. Focus on risk removal and Harmonization." [cite: 274-275]
* **The Harmonization Question:** "Why might this *not* work inside {customer_name}? Who are the internal blockers?" [cite: 276-277]
* **Risk Reversal:** "What do you need from us to feel safe moving to the next step?" [cite: 278]
"""

# --- UI LAYOUT ---
st.title("🎓 CRUSH Canonical Coach")
st.markdown("Generates a coaching guide based strictly on the **CRUSH — Sales Engagement (Canonical)** document.")

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

    submit = st.form_submit_button("Coach Me")

if submit:
    if not customer_name or not context:
        st.warning("⚠️ Please fill in Customer Name and Product Context.")
    else:
        with st.spinner(f"Analyzing Canonical Strategy for '{customer_name}'..."):
            final_prompt = MASTER_PROMPT.format(
                customer_name=customer_name,
                industry=industry,
                cdm_stage=cdm_stage,
                context=context
            )
            
            result_text = generate_guide(final_prompt)
            
            st.markdown(f"### 📋 Canonical Coaching Plan: {customer_name}")
            st.markdown(result_text)
