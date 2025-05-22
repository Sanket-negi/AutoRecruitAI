import streamlit as st
import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF for PDF text extraction

# ----------- Scrapers -----------

def scrape_internshala_jobs(role="Data Scientist", location="Remote"):
    role_slug = role.replace(" ", "-").lower()
    location_slug = location.lower().replace(" ", "-")
    url = f"https://internshala.com/internships/{role_slug}-internship-in-{location_slug}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    
    jobs = []
    for div in soup.find_all("div", class_="individual_internship"):
        title_tag = div.find("a", class_="view_detail_button")
        company_tag = div.find("a", class_="link_display_like_text")
        if not title_tag or not company_tag:
            continue
        title = title_tag.text.strip()
        company = company_tag.text.strip()
        link = "https://internshala.com" + title_tag["href"]
        jobs.append({"title": title, "company": company, "link": link, "source": "Internshala"})
    return jobs

def scrape_naukri_jobs(role="Data Scientist", location="Bangalore"):
    role_slug = role.replace(" ", "-").lower()
    location_slug = location.replace(" ", "-").lower()
    url = f"https://www.naukri.com/{role_slug}-jobs-in-{location_slug}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    jobs = []
    job_cards = soup.find_all("article", class_="jobTuple bgWhite br4 mb-8")
    
    for job in job_cards:
        title_tag = job.find("a", class_="title fw500 ellipsis")
        company_tag = job.find("a", class_="subTitle ellipsis fleft")
        location_tag = job.find("li", class_="fleft grey-text br2 placeHolderLi location")
        link = title_tag['href'] if title_tag else None
        if title_tag and company_tag and link:
            title = title_tag.text.strip()
            company = company_tag.text.strip()
            location = location_tag.text.strip() if location_tag else ""
            jobs.append({"title": title, "company": company, "location": location, "link": link, "source": "Naukri"})
    return jobs

# ----------- PDF Resume Parsing -----------

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# ----------- Streamlit UI -----------

st.title("Job Applying Companion")

st.markdown("""
Upload up to 3 resumes (PDF) for different profiles (e.g., AIML, SDE).  
Enter your preferred job role and location.  
The app will scrape recent job postings from Internshala and Naukri and show combined results.
""")

# Upload resumes
uploaded_files = st.file_uploader("Upload Resume PDFs", type=["pdf"], accept_multiple_files=True)
resumes_text = []
for i, file in enumerate(uploaded_files[:3]):
    text = extract_text_from_pdf(file)
    resumes_text.append({"filename": file.name, "text": text})

# Input job preferences
job_role = st.text_input("Desired Job Role", "Data Scientist")
job_location = st.text_input("Preferred Location", "Remote")

if st.button("Search Jobs"):
    with st.spinner("Scraping jobs from Internshala and Naukri..."):
        jobs_internshala = scrape_internshala_jobs(job_role, job_location)
        jobs_naukri = scrape_naukri_jobs(job_role, job_location)
        all_jobs = jobs_internshala + jobs_naukri
    
    st.success(f"Found {len(all_jobs)} jobs")
    
    for idx, job in enumerate(all_jobs[:50], 1):
        st.markdown(f"**{idx}. {job['title']}** - {job.get('company', 'N/A')} ({job.get('location', '')})  \n[{job['source']}]({job['link']})")

# ----------- Placeholder for LLM matching and message drafting -----------

st.markdown("---")
st.subheader("Next Steps (Future work)")
st.write("""
- Use LLM to **match each job posting to the best resume** uploaded  
- Use LLM to **generate personalized referral or application messages**  
- Add functionality to **fetch potential referrers' contacts** (emails/LinkedIn profiles)  
- Add **confirmation and automated application sending**
""")
