
from typing import List, Optional, Dict
import fitz
from pydantic import BaseModel
from utils import simple_match_score, generate_message_gemma
from langgraph.graph import StateGraph

SAMPLE_JOBS = [
    {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "location": "Remote",
        "description": "Develop software applications using Java, Python, and cloud technologies."
    },
    {
        "title": "Data Scientist",
        "company": "Data Inc",
        "location": "New York",
        "description": "Work on data analysis, machine learning models, and big data tools like Spark."
    },
    {
        "title": "BackEnd Developer",
        "company": "REAL DATA Ltd",
        "location": "Banglore",
        "description": "Worked on API Development , comfortable with Springboot , Spring , Next.js and Nodejs~~"   
    },
    {
        "title": "AI/ML Engineer",
        "company": "AI Labs",
        "location": "San Francisco",
        "description": "Build AI and ML solutions, Worked on Machine learning and Gen AI including langchain and RAGs, Python programming."
    }
]

class AppState(BaseModel):
    resumes: List[Dict]
    job_role: str
    jobs: List[Dict] = []
    matched_jobs: List[Dict]
    messages: List[str]
    error: Optional[str] = None

def fetch_jobs_node(state: AppState) -> AppState:
    try:
        state.jobs = scrape_naukri_jobs(query=state.job_role or "software engineer")
        state.error = None
    except Exception as e:
        state.error = str(e)
        state.jobs = []
    return state


def extract_text_node(state: AppState) -> AppState:
    extracted = []
    for r in state.resumes:
        doc = fitz.open(stream=r["content"], filetype="pdf")
        text = "".join([page.get_text() for page in doc])
        extracted.append({"filename": r["filename"], "text": text})
    state.resumes = extracted
    return state

def match_jobs_node(state: AppState) -> AppState:
    matched = []
    for job in SAMPLE_JOBS:
        best_score = 0
        best_resume = None
        for r in state.resumes:
            score = simple_match_score(r["text"], job["description"])
            if score > best_score:
                best_score = score
                best_resume = r
        matched.append({"job": job, "resume": best_resume, "score": best_score})
    state.matched_jobs = matched
    return state

def generate_messages_node(state: AppState) -> AppState:
    messages = []
    for match in state.matched_jobs:
        job = match["job"]
        resume = match["resume"]
        score = match["score"]
        
        if score < 5:
            # Custom message for low scores
            prompt = f"""You are a job application assistant of a HR named Ms Merry [Senior Executive HR].
            Behave like a professional HR
            Given this job description and resume, write a short job rejection application message, t=due to failure of satisfying some specific required skills.
            use correct job details provided below:
            
            Job Description:
            {job['description']}
            {job['company']} use this as company name
            {job['title']}
            Resume:
            {resume['text'][:1000]}
            
                Sincerely,
                Ms Merry
                Senior Executive HR
            """
            msg = generate_message_gemma(prompt)
        else:
            prompt = f"""
You are a job application assistant of a HR named Ms Merry[Senior Executive HR].
Behave like a professional HR
Given this job description and resume, write a short job application message.
use correct job details provided below:
Job Description:
{job['description']}
{job['company']}
{job['title']}

Resume:
{resume['text'][:1000]}
Sincerely,
Ms Merry
Senior Executive HR
"""
            msg = generate_message_gemma(prompt)
        
        messages.append(msg)
    state.messages = messages
    return state

def build_graph():
    builder = StateGraph(state_schema=AppState)
    builder.add_node("fetch_jobs", fetch_jobs_node)
    builder.add_node("extract", extract_text_node)
    builder.add_node("match", match_jobs_node)
    builder.add_node("generate", generate_messages_node)
    
    builder.set_entry_point("fetch_jobs")
    builder.add_edge("fetch_jobs", "extract")
    builder.add_edge("extract", "match")
    builder.add_edge("match", "generate")
    return builder.compile()
