import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="CRUSH Sales Coach", page_icon="🎓", layout="wide")

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
You are an expert Sales Coach mentoring a junior salesperson.
Your goal is to prepare them for a specific meeting with **{customer_name}**.

**THE SITUATION:**
The rep is nervous. They tend to "pitch features" too early.
You need to give them a **Narrative Playbook** that focuses on "Adoption Risk" (Fear) rather than just "Pain."

**CORE CRUSH PRINCIPLES TO TEACH:**
1.  [cite_start]**Parallel Paths:** The Company wants "Logic" (Goals), but the Person feels "Emotion" (Fear). [cite: 186-193]
2.  **The Trust Gateway:** Don't start with small talk. [cite_start]Start with a "Visual Agenda" to lower their anxiety (Cognitive Load). [cite: 258-259]
3.  **Harmonization:** Don't "close." [cite_start]Ask what will prevent this from working (Risk Removal). [cite: 275-277]

**INPUTS:**
- Customer: {customer_name} ({industry})
- Product/Context: {context}
- Stage: {cdm_stage}

**OUTPUT FORMAT (Markdown):**

## 🧠 Part 1: Get Your Head Right (Prep)
*Coach the rep on what is actually happening in this deal.*
* **The "Company" Logic:** Briefly explain what the business is trying to fix (e.g., Efficiency).
* **The "Person" Fear:** Explain what the human across the table is likely afraid of (e.g., "If I buy this and it fails, I look stupid").
* **Coach's Advice:** "Your job today is not to sell the product, but to sell the *safety* of the decision."

---

## 🗣️ Part 2: The Script & Flow

### The Opening (Don't Chat, Lead)
[cite_start]**Coach's Tip:** "Don't ask 'How are you?'. It signals you are an outsider. Instead, use a 'Visual Agenda' to show you are organized. This lowers their cortisol." [cite: 209-211]
* **The Script:** Write the exact opening lines:
    1.  **Context Hook:** "I was preparing for this call and thinking about [Industry Trend]..."
    2.  **The Agenda:** "To respect your time, I mapped out where we are (Current State), where you want to go (Destination), and the path between. Does that map to your thinking?"

### The Middle (The Pivot to Change)
**Coach's Tip:** "Stop pitching features. Pivot to the 'Unique Change Point'. Challenge them on why their current approach is risky."
* **The Bridge:** "Most companies in {industry} try to solve this by [Old Way], but they struggle because..."
* **The Question:** "How are you ensuring your team actually adopts this change, or is that the risk we need to solve?"

### The End (Harmonization, Not Closing)
**Coach's Tip:** "Do not ask for the order yet. That creates pressure. Instead, ask for the *blockers*. This is called Harmonization."
* **The Harmonization Question:** "This looks good on paper, but why might this *not* work inside {customer_name}?"
* **The Safe Close:** "Based on that, what do you need from us to feel safe moving to the next step?"
"""

# --- UI LAYOUT ---
st.title("🎓 CRUSH Sales Coach")
st.markdown("A virtual coach to prep you for your next meeting.")

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
        with st.spinner(f"Analyzing deal strategy for '{customer_name}'..."):
            final_prompt = MASTER_PROMPT.format(
                customer_name=customer_name,
                industry=industry,
                cdm_stage=cdm_stage,
                context=context
            )
            
            result_text = generate_guide(final_prompt)
            
            st.markdown(f"### 📋 Coaching Plan: {customer_name}")
            st.markdown(result_text)
