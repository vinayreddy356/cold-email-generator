import os
import json
import re
from json_repair import repair_json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

class Chain:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set.")
            
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=api_key,
            model_name="openai/gpt-oss-20b"
        )

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            
            ### INSTRUCTION:
            The scraped text is from the career page of a website.
            Extract all job postings and return them as a JSON list of objects.
            Each object MUST contain these exact keys: `role`, `experience`, `skills`, and `description`.
            Return ONLY valid raw JSON array. Do NOT wrap in markdown backticks.
            ### JSON OUTPUT:
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={'page_data': cleaned_text})
        
        raw_text = res.content.strip()
        repaired_string = repair_json(raw_text)
        
        try:
            parsed = json.loads(repaired_string)
        except Exception as e:
            raise ValueError(f"Failed to parse JSON even after repair. Raw output: {raw_text}") from e
                
        return parsed if isinstance(parsed, list) else [parsed]

    def write_email(self, job, links):
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}
            
            ### PORTFOLIO LINKS:
            {link_list}
            
            ### INSTRUCTION:
            You are Vinay, a Business Development Executive at AtliQ. AtliQ is a Software Consulting firm helping companies scale with AI, Cloud, and Software solutions.
            Your task is to write a cold email to the client describing how AtliQ can fulfill their needs based on the job description above.
            Incorporate relevant portfolio links ({link_list}) naturally to demonstrate capacity.
            Do NOT include placeholders like [Your Name]. Sign off as Vinay.
            ### EMAIL (NO PREAMBLE):
            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link_list": links})
        return res.content

    # Alias write_mail to write_email so either name works without breaking
    write_mail = write_email