import streamlit as st
from transformers import pipeline

# Load API key from Streamlit secrets
huggingface_api_key = st.secrets["HUGGINGFACE_API_KEY"]

# Use a smaller model to prevent crashes
generator = pipeline(
    "text-generation",
    model="facebook/opt-1.3b",  # Change to a smaller model
    use_auth_token=huggingface_api_key,  # ✅ Correct authentication
    device=0  # ✅ Use GPU if available, set to -1 for CPU
)

# Streamlit UI
st.title("Resume Analyzer - AI Powered")

resume_text = st.text_area("Paste Resume Text Here")
job_description = st.text_area("Paste Job Description Here")

if st.button("Analyze Resume"):
    if resume_text and job_description:
        prompt = f"Analyze this resume for the given job description:\nResume: {resume_text}\nJob: {job_description}"
        response = generator(prompt, max_length=300, num_return_sequences=1)
        st.subheader("AI Analysis:")
        st.write(response[0]['generated_text'])
    else:
        st.warning("Please enter both Resume and Job Description!")
