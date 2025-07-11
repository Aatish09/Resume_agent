import streamlit as st
from utils.database import DatabaseManager
from utils.ai_agents import AIAgents, ResumeState
from utils.resume_generator import ResumeGenerator
import time

st.set_page_config(layout="wide")
st.title("🚀 Generate a Tailored Resume")

if not st.session_state.get('user_id'):
    st.warning("Please log in from the main page to generate a resume.")
    st.stop()

# Initialize managers
db_manager = DatabaseManager()
ai_agents = AIAgents()
resume_gen = ResumeGenerator()

# UI
jd_text = st.text_area("Paste the Job Description Here", height=300)

if st.button("Generate Resume", type="primary"):
    if not jd_text.strip():
        st.error("Please paste a job description.")
    else:
        with st.spinner("Your personalized resume is being crafted by AI..."):
            start_time = time.time()
            
            # 1. Fetch all user data from DB
            user_profile = db_manager.get_user_profile(st.session_state.user_id)
            user_profile['education'] = db_manager.get_education(st.session_state.user_id)
            
            all_experiences = db_manager.get_work_experiences(st.session_state.user_id)
            all_projects = db_manager.get_projects(st.session_state.user_id)
            all_skills = db_manager.get_skills(st.session_state.user_id)
            
            # 2. Compile and run the LangGraph workflow
            workflow = ai_agents.create_resume_workflow()
            initial_state: ResumeState = {
                "user_id": st.session_state.user_id,
                "job_description": jd_text,
                "user_profile": user_profile,
                "all_experiences": all_experiences,
                "all_projects": all_projects,
                "all_skills": all_skills,
                "jd_analysis": {},
                "selected_experiences": [],
                "selected_projects": [],
                "selected_skills": [],
                "tailored_summary": "",
                "tailored_experiences": [],
                "tailored_projects": [],
                "company_info": {},
                "resume_content": ""
            }
            
            final_state = workflow.invoke(initial_state)
            
            # 3. Generate the PDF from the final state
            pdf_bytes, markdown_content = resume_gen.create_pdf(final_state)
            
            # 4. Save the result to the database
            db_manager.save_generated_resume({
                "user_id": st.session_state.user_id,
                "job_title": final_state['jd_analysis'].get('job_title', 'N/A'),
                "company_name": final_state['jd_analysis'].get('company_name', 'N/A'),
                "job_description": jd_text,
                "jd_analysis": final_state['jd_analysis'],
                "tailored_summary": final_state['tailored_summary'],
                "markdown_source": markdown_content
            })
            
            end_time = time.time()
            st.success(f"Resume generated in {end_time - start_time:.2f} seconds!")

            # 5. Display results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("✅ Your Resume is Ready!")
                st.download_button(
                    label="Download Resume (PDF)",
                    data=pdf_bytes,
                    file_name=f"Resume_{final_state['jd_analysis'].get('company_name', 'Company')}.pdf",
                    mime="application/pdf"
                )
                
                st.subheader("💡 Tailored Summary")
                st.info(final_state['tailored_summary'])
                
            with col2:
                st.subheader("🔍 Job Analysis")
                st.json({
                    "Job Title": final_state['jd_analysis'].get('job_title'),
                    "Company": final_state['jd_analysis'].get('company_name'),
                    "Required Skills": final_state['jd_analysis'].get('required_skills'),
                    "ATS Keywords": final_state['jd_analysis'].get('keywords')
                })
