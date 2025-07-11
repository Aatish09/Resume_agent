import streamlit as st
from utils.database import DatabaseManager
from utils.resume_generator import ResumeGenerator
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Generated Resume History")

if not st.session_state.get('user_id'):
    st.warning("Please log in from the main page to view your history.")
    st.stop()

db_manager = DatabaseManager()
resume_gen = ResumeGenerator() # Needed to re-generate PDF from markdown

resumes = db_manager.get_generated_resumes(st.session_state.user_id)

if not resumes:
    st.info("You haven't generated any resumes yet. Go to the 'Generate Resume' page to get started!")
else:
    # Display as a table
    df = pd.DataFrame(resumes)
    st.dataframe(df[['created_at', 'company_name', 'job_title']])

    st.divider()

    # Display details in expanders
    for resume in resumes:
        with st.expander(f"{resume['company_name']} - {resume['job_title']} ({pd.to_datetime(resume['created_at']).strftime('%Y-%m-%d')})"):
            st.subheader("Tailored Summary")
            st.info(resume.get('tailored_summary', 'No summary found.'))
            
            st.subheader("Job Analysis")
            st.json(resume.get('jd_analysis', {}))
            
            # Re-generate PDF on demand
            if st.button("Re-download PDF", key=f"download_{resume['id']}"):
                # This is a placeholder since we don't have the full state
                # A better approach is to store the markdown and regenerate
                markdown_source = resume.get("markdown_source")
                if markdown_source:
                    # We can't perfectly recreate the PDF as we don't have the full state,
                    # but we can from the stored markdown.
                    html_content = markdown2.markdown(markdown_source, extras=["tables"])
                    css = resume_gen.css_style
                    pdf_bytes = resume_gen.HTML(string=html_content).write_pdf(stylesheets=[resume_gen.CSS(string=css)])
                    
                    st.download_button(
                        label="Click to Download Again",
                        data=pdf_bytes,
                        file_name=f"Resume_{resume['company_name']}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("Could not re-generate PDF. Markdown source not found.")
