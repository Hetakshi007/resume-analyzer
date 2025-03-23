import streamlit as st
import re
import PyPDF2
import google.generativeai as genai
import pandas as pd

# Configure Google Gemini API
import os
genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 
model = genai.GenerativeModel('gemini-1.5-pro')

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

# Function to extract details from resume
def extract_details(resume_text):
    # Fallback name extraction using regex
    name_match = re.search(r"\b[A-Z][a-z]+\s[A-Z][a-z]+\b", resume_text)
    name = name_match.group(0) if name_match else "Unknown"

    # Gender Extraction
    gender_match = re.search(r"(Male|Female|Other)", resume_text, re.IGNORECASE)
    gender = gender_match.group(0) if gender_match else "Unknown"

    # Date of Birth Extraction
    dob_match = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", resume_text)
    dob = dob_match.group(0) if dob_match else "Unknown"

    # Generative AI Prompt for Extracting More Details
    prompt = f"Extract the following details from the resume text:\n\nSkills:\nEducational Qualifications:\nWork Experience:\nProjects:\nResearch:\n\nResume Text:\n{resume_text}"
    response = model.generate_content(prompt)
    extracted_details = response.text

    return {
        "Name": name,
        "Gender": gender,
        "Date of Birth": dob,
        "Details": extracted_details
    }

# Function to Generate Feedback & Job Suggestions
def generate_feedback_and_suggestions(resume_text, job_description):
    # Resume Improvement Feedback
    feedback_prompt = f"Provide detailed feedback on how to improve this resume for the job description:\n\nResume:\n{resume_text}\n\nJob Description:\n{job_description}"
    feedback_response = model.generate_content(feedback_prompt)
    feedback = feedback_response.text

    # Job Suggestions
    suggestions_prompt = f"Suggest job roles suitable for this resume:\n\nResume:\n{resume_text}"
    suggestions_response = model.generate_content(suggestions_prompt)
    suggestions = suggestions_response.text

    return feedback, suggestions

# Streamlit UI
st.title("Resume Analyzer")
st.write("Upload your resume in PDF format to analyze and get personalized feedback.")

# File Upload Section
uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
job_description = st.text_area("Enter the job description:")

if st.button("Analyze"):
    if uploaded_file and job_description:
        with open("temp_resume.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())

        resume_text = extract_text_from_pdf("temp_resume.pdf")
        details = extract_details(resume_text)

        st.subheader("Extracted Details")

        # Convert dictionary to DataFrame and remove index column
        details_df = pd.DataFrame(details.items(), columns=["Field", "Value"])

        # Fix alignment issue using st.markdown
        st.markdown(
            details_df.style.hide(axis="index").set_table_styles(
                [{"selector": "td", "props": [("text-align", "left")]}]
            ).to_html(),
            unsafe_allow_html=True
        )

        feedback, suggestions = generate_feedback_and_suggestions(resume_text, job_description)

        st.subheader("Feedback for Resume Improvement")
        st.write(feedback)

        st.subheader("Suggested Job Opportunities")
        st.write(suggestions)
