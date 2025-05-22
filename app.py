# app.py
from pipeline import build_graph, AppState
import streamlit as st

graph = build_graph()

st.title("AutoRecruitAI - Your Auto Recruiting Assistant")

uploaded_files = st.sidebar.file_uploader("Upload PDF resumes", accept_multiple_files=True)
resumes = []
for f in uploaded_files or []:
    resumes.append({
        "filename": f.name,
        "content": f.read()
    })

job_role = st.text_input("Job Role", "Software Engineer")

if st.button("Search Specific Job Role"):
    if not resumes:
        st.warning("Upload at least one resume!")
    else:
        initial_state: AppState = {
            "resumes": resumes,
            "job_role": job_role,
            "matched_jobs": [],
            "messages": [],
            "error": None
        }

        final_state = graph.invoke(initial_state)

        for i, result in enumerate(final_state["matched_jobs"]):
            job = result["job"]
            st.markdown(f"### {job['title']} at {job['company']} ({job['location']})")
            st.write(f"**Description:** {job['description']}")
            st.write(f"**Best Match:** {result['resume']['filename']} (Score: {result['score']})")
            st.text_area("Generated Message", value=final_state["messages"][i], height=150)
