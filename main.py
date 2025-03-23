import streamlit as st
import re
import PyPDF2
import google.generativeai as genai
import pandas as pd

# Configure Gemini AI API Key
import os
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text.strip()

# Function to extract details from resume text
def extract_details(resume_text):
    # Improved Name Extraction (Avoids "Consumer Sensitive")
    name_pattern = r"\b[A-Z][a-z]+(?:\s[A-Z]\.)?\s[A-Z][a-z]+\b"
    name = re.search(name_pattern, resume_text)
    name = name.group(0) if name else "Unknown"

    # Extract Gender
    gender = re.search(r"\b(Male|Female|Other)\b", resume_text, re.IGNORECASE)
    gender = gender.group(0).capitalize() if gender else "Unknown"

    # Extract Date of Birth (Supports multiple formats)
    dob_pattern = r"\b(?:\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})\b"
    dob = re.search(dob_pattern, resume_text)
    dob = dob.group(0) if dob else "Unknown"

    # Updated Prompt to Prevent "Consumer Sensitive" Issue
    prompt = f"""Extract the following details from the resume text:
    - Skills
    - Educational Qualifications
    - Work Experience
    - Projects
    - Research
    **Do not mark any name as "Consumer Sensitive"**

    Resume Text:
    {resume_text}"""

    response = model.generate_content(prompt)
    extracted_details = response.text

    return {
        "Name": name,
        "Gender": gender,
        "Date of Birth": dob,
        "Details": extracted_details
    }

# Function to calculate resume score
def calculate_score(details):
    score = 0
    score += min(details["Details"].count("Skills:"), 6) * 5
    score += min(details["Details"].count("Educational Qualifications:"), 5) * 4
    score += min(details["Details"].count("Work Experience:"), 5) * 5
    score += min(details["Details"].count("Projects:"), 5) * 3
    score += min(details["Details"].count("Research:"), 5) * 2
    return min(score, 100)

# Function to generate feedback & suggestions based on job description
def generate_feedback_and_suggestions(resume_text, job_description):
    feedback_prompt = f"Provide feedback to improve the following resume for the job description:\n\nResume:\n{resume_text}\n\nJob Description:\n{job_description}"
    feedback_response = model.generate_content(feedback_prompt)
    feedback = feedback_response.text

    suggestions_prompt = f"Suggest job opportunities and roles suitable for the following resume:\n\nResume:\n{resume_text}"
    suggestions_response = model.generate_content(suggestions_prompt)
    suggestions = suggestions_response.text

    return feedback, suggestions

# Streamlit UI
st.title("Resume Analyzer")
st.write("Upload your resume in PDF format to analyze and get personalized feedback.")

# Job Description Input (Always Visible)
job_description = st.text_area("Enter the job description:")

# Resume Upload
uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")

if uploaded_file:
    with open("temp_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    resume_text = extract_text_from_pdf("temp_resume.pdf")
    details = extract_details(resume_text)

    # Display Extracted Details
    details_df = pd.DataFrame(details.items(), columns=["Field", "Value"])
    details_df = details_df[details_df["Field"] != "Details"]  # Remove extra details row
    st.subheader("Extracted Details")
    st.table(details_df)

# Analyze Button (Works only if both Resume & Job Description are provided)
if uploaded_file and job_description and st.button("Analyze"):
    feedback, suggestions = generate_feedback_and_suggestions(resume_text, job_description)

    # Display Resume Score
    score = calculate_score(details)
    st.subheader(f"Resume Score: {score}/100")

    st.subheader("Feedback for Resume Improvement")
    st.write(feedback)

    st.subheader("Suggested Job Opportunities")
    st.write(suggestions)
