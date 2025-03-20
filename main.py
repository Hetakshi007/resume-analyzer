from transformers import pipeline
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("HUGGINGFACE_API_KEY")

# Authenticate Hugging Face API key
generator = pipeline(
    "text-generation",
    model="tiiuae/falcon-7b-instruct"
,
    token=api_key
)

def analyze_resume(resume_text, job_description):
    prompt = f"Analyze this resume for the given job description:\nResume: {resume_text}\nJob: {job_description}"
    response = generator(prompt, max_length=500, num_return_sequences=1)
    return response[0]['generated_text']

# Example test
resume_text = "Experienced data scientist with skills in Python and Machine Learning."
job_description = "Looking for an AI Engineer skilled in LLMs and NLP."

print(analyze_resume(resume_text, job_description))
