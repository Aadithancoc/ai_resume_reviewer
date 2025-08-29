import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Resume Reviewer", page_icon="📃", layout="centered")

st.title("AI Resume Reviewer")
st.markdown("Upload your resume and get AI-powered feedback tailored to your needs!")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

uploaded_file = st.file_uploader(
    "📂 Upload your resume (PDF or TXT)", 
    type=["pdf", "txt"]
)

def extract_text_from_pdf(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file()))
    return uploaded_file.read().decode("utf-8")


def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
       pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
       text = ""
       for page in pdf_reader.pages:
           text += page.extract_text()or ""
       return text
    else:
        return uploaded_file.read().decode("utf-8", errors="ignore") # type: ignore
    
job_role = st.text_input("Enter the job role you are targetting (optional)")
analyze = st.button("Analyze Resume")

if analyze and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("File does not have any content...")
            st.stop

        prompt = f"""Please analyze this resume and provide constructive feedback.
        Focus on the following aspects:
        1. Content clarity and impact
        2. Skills presentation
        3. Experience descriptions
        4. Specific improvements for {job_role if job_role else 'general job applications'}

        Resume content:
        {file_content}

        Please provide your analysis in a clear, structured format with specific recommendations with bullet points.Finally, give an overall rating out of 10 for the resume (e.g., 7/10)"""

        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an expert resume reviewer with years of experience in HR and recruitment."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        st.markdown("### Analysis Results")
        st.markdown(response.choices[0].message.content)
    except Exception as e:
        st.error(f"An error occured: {str(e)}")