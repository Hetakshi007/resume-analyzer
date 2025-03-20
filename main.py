import streamlit as st
from transformers import pipeline

# Load API key from Streamlit secrets
huggingface_api_key = st.secrets["HUGGINGFACE_API_KEY"]

# Initialize the model
generator = pipeline("text-generation", model="tiiuae/falcon-7b-instruct", token=huggingface_api_key)

# Streamlit UI
st.title("Resume Analyzer - AI Powered")

resume_text = st.text_area("Paste Resume Text Here")
job_description = st.text_area("Paste Job Description Here")

if st.button("Analyze Resume"):
    if resume_text and job_description:
        prompt = f"Analyze this resume for the given job description:\nResume: {resume_text}\nJob: {job_description}"
        response = generator(prompt, max_length=500, num_return_sequences=1)
        st.subheader("AI Analysis:")
        st.write(response[0]['generated_text'])
    else:
        st.warning("Please enter both Resume and Job Description!")
