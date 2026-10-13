import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text

def create_streamlit_app(chain, portfolio, clean_text):
    st.title("📧 Cold Mail Generator")
    
    # Input selection option for public URLs vs login-protected posts like LinkedIn
    input_type = st.radio(
        "Choose Input Method:",
        ["Public URL (Lever, Greenhouse, Nike, etc.)", "Paste Job Description Text (LinkedIn, Indeed, etc.)"]
    )
    
    if "Public URL" in input_type:
        url_input = st.text_input("Enter Job Page URL:", value="https://jobs.nike.com/job/R-33460")
        submit_button = st.button("Generate Email from URL")
        
        if submit_button:
            if not url_input.strip():
                st.warning("Please enter a valid URL.")
                return
            try:
                with st.spinner("Scraping webpage and extracting job details..."):
                    loader = WebBaseLoader([url_input])
                    raw_content = loader.load().pop().page_content
                    data = clean_text(raw_content)
                    portfolio.load_portfolio()
                    jobs = chain.extract_jobs(data)
                    
                    for job in jobs:
                        skills = job.get('skills', [])
                        links = portfolio.query_links(skills)
                        email = chain.write_email(job, links)
                        st.subheader(f"Generated Cold Email for: {job.get('role', 'Target Role')}")
                        st.code(email, language='markdown')
            except Exception as e:
                st.error(f"An error occurred while scraping: {e}")

    else:
        text_input = st.text_area(
            "Paste Raw Job Description Text:",
            height=250,
            placeholder="Paste job title, experience level, required skills, and description here..."
        )
        submit_button = st.button("Generate Email from Text")
        
        if submit_button:
            if not text_input.strip():
                st.warning("Please paste a job description first.")
                return
            try:
                with st.spinner("Extracting job details and matching portfolio..."):
                    data = clean_text(text_input)
                    portfolio.load_portfolio()
                    jobs = chain.extract_jobs(data)
                    
                    for job in jobs:
                        skills = job.get('skills', [])
                        links = portfolio.query_links(skills)
                        email = chain.write_email(job, links)
                        st.subheader(f"Generated Cold Email for: {job.get('role', 'Target Role')}")
                        st.code(email, language='markdown')
            except Exception as e:
                st.error(f"An error occurred while processing text: {e}")

if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    
    # Initialize chains & vector DB
    chain = Chain()
    portfolio = Portfolio()
    
    create_streamlit_app(chain, portfolio, clean_text)