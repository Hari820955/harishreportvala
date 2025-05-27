import streamlit as st
import pytesseract
from PIL import Image
import cv2
import numpy as np
from googletrans import Translator
import re
from langdetect import detect

st.set_page_config(page_title="Reportslelo", layout="centered")

def extract_text_from_image(uploaded_file):
    image = Image.open(uploaded_file).convert("RGB")
    image_np = np.array(image)
    text = pytesseract.image_to_string(image_np)
    return text

def extract_patient_info(text):
    name = re.search(r"(?:Name|Naam|Patient)\s*[:\-]?\s*([A-Za-z\s.]+)", text, re.IGNORECASE)
    age = re.search(r"(?:Age|Umar)\s*[:\-]?\s*(\d{1,3})", text, re.IGNORECASE)
    phone = re.search(r"(\+91[-\s]?\d{10}|\b\d{10}\b)", text)

    return {
        "name": name.group(1).strip() if name else "Mr/Ms",
        "age": age.group(1) + " साल" if age else "N/A",
        "contact": phone.group(1) if phone else "N/A"
    }

def generate_hindi_summary(text):
    translator = Translator()
    summary_english = ""

    if "high" in text.lower() or "elevated" in text.lower() or "abnormal" in text.lower():
        summary_english = "Some values in the report seem higher than normal. Please consult a doctor immediately."
    elif "low" in text.lower() or "deficiency" in text.lower():
        summary_english = "Some values in the report seem lower than normal. A medical consultation is advised."
    elif "positive" in text.lower() and "negative" not in text.lower():
        summary_english = "The report shows a positive result. Further diagnosis may be necessary."
    else:
        summary_english = "The report appears mostly normal. However, consult a doctor if you feel unwell."

    try:
        translated = translator.translate(summary_english, dest='hi')
        return translated.text
    except:
        return "रिपोर्ट सामान्य लग रही है। किसी भी शंका में डॉक्टर से सलाह लें।"

st.title("🧾 Reportslelo - Lab Report Summary AI")
uploaded_file = st.file_uploader("कोई भी लैब रिपोर्ट इमेज अपलोड करें", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file:
    with st.spinner("रिपोर्ट पढ़ी जा रही है..."):
        extracted_text = extract_text_from_image(uploaded_file)
        patient = extract_patient_info(extracted_text)
        hindi_summary = generate_hindi_summary(extracted_text)

        st.subheader("📜 रिपोर्ट से निकाला गया टेक्स्ट:")
        st.text_area("", extracted_text, height=300)

        st.subheader("📩 मरीज को भेजा जाने वाला हिंदी मैसेज:")
        final_message = f"""
👤 नाम: {patient['name']}
🎂 उम्र: {patient['age']}
📱 संपर्क: {patient['contact']}

📑 रिपोर्ट का सारांश:
{hindi_summary}

🏥 Harish Choudhary Clinic
📞 8209558359
"""
        st.text_area("मैसेज कॉपी करें:", final_message, height=250)
