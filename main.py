import streamlit as st
import re
import PyPDF2
import google.generativeai as genai
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import os
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_details(resume_text):
    name = re.search(r"([A-Z][a-z]+ [A-Z][a-z]+)", resume_text)
    name = name.group(0) if name else "Unknown"

    gender = re.search(r"(Male|Female|Other)", resume_text, re.IGNORECASE)
    gender = gender.group(0) if gender else "Unknown"

    dob = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", resume_text)
    dob = dob.group(0) if dob else "Unknown"

    prompt = f"Extract the following details from the resume text:\n\nSkills:\nEducational Qualifications:\nWork Experience:\nProjects:\nResearch:\n\nResume Text:\n{resume_text}"
    response = model.generate_content(prompt)
    extracted_details = response.text

    return {
        "Name": name,
        "Gender": gender,
        "Date of Birth": dob,
        "Details": extracted_details
    }

def calculate_score(details):
    score = 0
    skills = details["Details"].count("Skills:")
    score += min(skills * 5, 30)

    education = details["Details"].count("Educational Qualifications:")
    score += min(education * 4, 20)

    experience = details["Details"].count("Work Experience:")
    score += min(experience * 5, 25)

    projects = details["Details"].count("Projects:")
    score += min(projects * 3, 15)

    research = details["Details"].count("Research:")
    score += min(research * 2, 10)

    return score

def generate_feedback_and_suggestions(resume_text, job_description):
    feedback_prompt = f"Provide feedback to improve the following resume for the job description:\n\nResume:\n{resume_text}\n\nJob Description:\n{job_description}"
    feedback_response = model.generate_content(feedback_prompt)
    feedback = feedback_response.text

    suggestions_prompt = f"Suggest job opportunities and roles suitable for the following resume:\n\nResume:\n{resume_text}"
    suggestions_response = model.generate_content(suggestions_prompt)
    suggestions = suggestions_response.text

    return feedback, suggestions

st.title("Resume Analyzer and Skill Enhancement Recommender")
st.write("Upload your resume in PDF format to analyze and get personalized feedback.")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")

if uploaded_file is not None:
    with open("temp_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    resume_text = extract_text_from_pdf("temp_resume.pdf")
    details = extract_details(resume_text)

    st.subheader("Extracted Details")
    st.table(pd.DataFrame(list(details.items()), columns=["Field", "Value"]))

    score = calculate_score(details)
    st.subheader(f"Resume Score: {score}/100")

    st.subheader("Reason for Score")
    st.write("The score is calculated based on the following criteria:")
    st.write("- **Skills**: 5 points per skill (max 30)")
    st.write("- **Education**: 4 points per qualification (max 20)")
    st.write("- **Work Experience**: 5 points per experience (max 25)")
    st.write("- **Projects**: 3 points per project (max 15)")
    st.write("- **Research**: 2 points per research (max 10)")

    job_description = "Looking for a software engineer with expertise in Python, Java, and machine learning."
    feedback, suggestions = generate_feedback_and_suggestions(resume_text, job_description)

    st.subheader("Feedback for Resume Improvement")
    st.write(feedback)

    st.subheader("Suggested Job Opportunities")
    st.write(suggestions)
