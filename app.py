import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract
import re
import datetime
import io
import requests
from docx import Document
import os
from dotenv import load_dotenv

# ────────────────────────────────
# LOAD ENV (API KEY SAFE STORAGE)
# ────────────────────────────────
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ────────────────────────────────
# OCR CONFIG
# ────────────────────────────────
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ────────────────────────────────
# PAGE CONFIG
# ────────────────────────────────
st.set_page_config(
    page_title="🔐 Agentic OCR System",
    page_icon="🔐",
    layout="wide"
)

# ────────────────────────────────
# BEIGE UI THEME
# ────────────────────────────────
st.markdown("""
<style>

.stApp {
    background: linear-gradient(to bottom right, #f6efe7, #efe2d1);
    color: #3b2f24;
}

/* TITLE */
.title {
    font-size: 42px;
    font-weight: 900;
    text-align: center;
    color: #4a3a2a;
}

/* SUBTITLE */
.subtitle {
    text-align: center;
    color: #7a6250;
    margin-bottom: 20px;
}

/* CARD */
.card {
    background: #fff7ec;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #e6d2b8;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.08);
}

/* METRICS */
.metric {
    background: linear-gradient(135deg, #f7ead7, #f3e2c6);
    padding: 18px;
    border-radius: 16px;
    text-align: center;
    border: 1px solid #e2c9a6;
}

.metric h2 {
    margin: 0;
    color: #4a3a2a;
}

/* BUTTON */
.stButton>button {
    background: #d6b98c;
    color: white;
    border-radius: 10px;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background-color: #eadcc9;
}

</style>
""", unsafe_allow_html=True)

# ────────────────────────────────
# HEADER
# ────────────────────────────────
st.markdown('<div class="title">🔐 Agentic OCR System</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Beige Secure AI • OCR • Privacy Shield • Intelligence Layer</div>', unsafe_allow_html=True)

# ────────────────────────────────
# CONSENT SYSTEM (IMPORTANT)
# ────────────────────────────────
st.sidebar.markdown("## ⚙️ Privacy Consent")

consent = st.sidebar.checkbox("✔ I confirm I have permission to process this document")

mode = st.sidebar.selectbox("Mode", ["Secure Redaction", "Detection Only"])

if not consent:
    st.warning("⚠️ Please provide consent to continue. This system processes sensitive data.")
    st.stop()

# ────────────────────────────────
# PATTERNS (PRIVACY SHIELD)
# ────────────────────────────────
PATTERNS = {
    "CNIC": (r"\b\d{5}-\d{7}-\d{1}\b", "█████-███████-█"),
    "EMAIL": (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "████@████.██"),
    "PHONE": (r"\b03\d{2}-?\d{7}\b", "03██-███████"),
}

# ────────────────────────────────
# IMAGE PREPROCESSING
# ────────────────────────────────
def preprocess(img):
    img = ImageOps.grayscale(img)
    img = img.resize((img.width * 2, img.height * 2))
    img = img.filter(ImageFilter.MedianFilter())
    img = img.filter(ImageFilter.SHARPEN)
    img = ImageEnhance.Contrast(img).enhance(3)
    return img

# ────────────────────────────────
# OCR ENGINE
# ────────────────────────────────
def extract_text(img):
    img = preprocess(img)
    text = pytesseract.image_to_string(img, config="--oem 3 --psm 6")
    text = re.sub(r"[^A-Za-z0-9@.\-:/ ]+", " ", text)
    return text.strip()

# ────────────────────────────────
# PRIVACY SHIELD
# ────────────────────────────────
def shield(text):
    findings = []
    redacted = text

    for label, (pattern, mask) in PATTERNS.items():
        matches = re.findall(pattern, redacted)
        for m in matches:
            findings.append({"type": label, "value": m})
        redacted = re.sub(pattern, mask, redacted)

    return redacted, findings

# ────────────────────────────────
# GROQ AI
# ────────────────────────────────
def call_groq(text):

    if not GROQ_API_KEY:
        return {"error": "Missing API Key in .env"}

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-70b-versatile",
        "messages": [
            {"role": "system", "content": "You analyze OCR documents and extract structured insights."},
            {"role": "user", "content": text}
        ],
        "temperature": 0.2
    }

    res = requests.post(url, json=payload, headers=headers)
    return res.json()

# ────────────────────────────────
# FILE UPLOAD
# ────────────────────────────────
file = st.file_uploader("📤 Upload Document", type=["png", "jpg", "jpeg"])

if file:

    img = Image.open(file)

    raw = extract_text(img)
    redacted, findings = shield(raw)
    ai_output = call_groq(redacted)

    # ───── DASHBOARD ─────
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric">
        <h2>{len(findings)}</h2>
        <p>Privacy Leaks</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        status = "SAFE" if len(findings) == 0 else "REDACTED"
        st.markdown(f"""
        <div class="metric">
        <h2>{status}</h2>
        <p>Status</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric">
        <h2>{mode}</h2>
        <p>Mode</p>
        </div>
        """, unsafe_allow_html=True)

    # ───── IMAGE ─────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.image(img, caption="Uploaded Document", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ───── OUTPUT ─────
    st.subheader("📄 OCR Text")
    st.write(raw)

    st.subheader("🛡️ Redacted Text")
    st.write(redacted)

    st.subheader("🚨 Findings")
    st.json(findings)

    st.subheader("🧠 AI Analysis")
    st.json(ai_output)

# ────────────────────────────────
# FOOTER
# ────────────────────────────────
st.markdown("---")
st.caption("🔐 Privacy-first OCR System • Ethical AI with Consent Control")