import streamlit as st
from utils.database import DatabaseManager
from datetime import date

st.set_page_config(layout="wide")
st.title("📋 Profile Setup")

db_manager = DatabaseManager()

if not st.session_state.get('user_id'):
    st.warning("Please log in from the main page to set up your profile.")
    st.stop()

# --- Profile Section ---
st.header("👤 Basic Information")
profile = db_manager.get_user_profile(st.session_state.user_id) or {}

with st.form("profile_form"):
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Full Name*", value=profile.get('full_name', ''))
        email = st.text_input("Email", value=profile.get('email', st.session_state.get('user_email', '')), disabled=True)
        phone = st.text_input("Phone Number", value=profile.get('phone', ''))
        location = st.text_input("Location (City, State)", value=profile.get('location', ''))
    with col2:
        linkedin_url = st.text_input("LinkedIn URL", value=profile.get('linkedin_url', ''))
        github_url = st.text_input("GitHub URL", value=profile.get('github_url', ''))
        portfolio_url = st.text_input("Portfolio URL", value=profile.get('portfolio_url', ''))
        years_exp = st.number_input("Years of Experience", min_value=0, value=profile.get('years_of_experience', 0))

    if st.form_submit_button("Save Profile"):
        updates = {
            "full_name": full_name,
            "phone": phone,
            "location": location,
            "linkedin_url": linkedin_url,
            "github_url": github_url,
            "portfolio_url": portfolio_url,
            "years_of_experience": years_exp
        }
        if profile:
            db_manager.update_user_profile(st.session_state.user_id, updates)
        else:
            updates['id'] = st.session_state.user_id
            updates['email'] = st.session_state.user_email
            db_manager.create_user_profile(updates)
        st.success("Profile saved!")
        st.rerun()

st.divider()

# --- Data Management Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["💼 Work Experience", "🚀 Projects", "🎓 Education", "🛠️ Skills", "🏅 Certifications"])

# Work Experience Tab
with tab1:
    st.subheader("Add/Edit Work Experience")
    with st.expander("Add New Experience", expanded=False):
        with st.form("work_exp_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            company = c1.text_input("Company*")
            position = c2.text_input("Position*")
            location = c1.text_input("Location")
            start_date = c1.date_input("Start Date", date(2020, 1, 1))
            end_date = c2.date_input("End Date", date(2022, 1, 1))
            is_current = c2.checkbox("Currently work here")
            achievements = st.text_area("Key Achievements (one per line)")
            technologies = st.text_input("Technologies (comma-separated)")

            if st.form_submit_button("Add Experience"):
                if company and position:
                    db_manager.add_work_experience({
                        "user_id": st.session_state.user_id,
                        "company_name": company, "position": position, "location": location,
                        "start_date": str(start_date), "end_date": str(end_date) if not is_current else None,
                        "is_current": is_current,
                        "achievements": [a.strip() for a in achievements.split('\n') if a.strip()],
                        "technologies": [t.strip() for t in technologies.split(',') if t.strip()]
                    })
                    st.success("Experience Added!")
                    st.rerun()

    st.subheader("Your Experiences")
    experiences = db_manager.get_work_experiences(st.session_state.user_id)
    for exp in experiences:
        with st.container(border=True):
            st.markdown(f"**{exp['position']}** at **{exp['company_name']}**")
            if st.button("Delete", key=f"del_exp_{exp['id']}"):
                db_manager.delete_work_experience(exp['id'])
                st.rerun()

# Projects Tab
with tab2:
    st.subheader("Add/Edit Projects")
    with st.expander("Add New Project", expanded=False):
        with st.form("project_form", clear_on_submit=True):
            title = st.text_input("Title*")
            achievements = st.text_area("Key Features/Achievements (one per line)")
            technologies = st.text_input("Technologies (comma-separated)")
            
            if st.form_submit_button("Add Project"):
                if title:
                    db_manager.add_project({
                        "user_id": st.session_state.user_id, "title": title,
                        "achievements": [a.strip() for a in achievements.split('\n') if a.strip()],
                        "technologies": [t.strip() for t in technologies.split(',') if t.strip()]
                    })
                    st.success("Project Added!")
                    st.rerun()

    st.subheader("Your Projects")
    projects = db_manager.get_projects(st.session_state.user_id)
    for proj in projects:
        with st.container(border=True):
            st.markdown(f"**{proj['title']}**")
            if st.button("Delete", key=f"del_proj_{proj['id']}"):
                db_manager.delete_project(proj['id'])
                st.rerun()

# Education Tab
with tab3:
    st.subheader("Add/Edit Education")
    with st.expander("Add New Education", expanded=False):
        with st.form("edu_form", clear_on_submit=True):
            institution = st.text_input("Institution*")
            degree = st.text_input("Degree*")
            field = st.text_input("Field of Study")
            start_date = st.date_input("Start Date", date(2016, 9, 1))
            end_date = st.date_input("End Date", date(2020, 5, 1))
            
            if st.form_submit_button("Add Education"):
                if institution and degree:
                    db_manager.add_education({
                        "user_id": st.session_state.user_id, "institution": institution,
                        "degree": degree, "field_of_study": field,
                        "start_date": str(start_date), "end_date": str(end_date)
                    })
                    st.success("Education Added!")
                    st.rerun()

    st.subheader("Your Education")
    education_list = db_manager.get_education(st.session_state.user_id)
    for edu in education_list:
        with st.container(border=True):
            st.markdown(f"**{edu['degree']}** from **{edu['institution']}**")
            if st.button("Delete", key=f"del_edu_{edu['id']}"):
                db_manager.delete_education(edu['id'])
                st.rerun()

# Skills Tab
with tab4:
    st.subheader("Add/Edit Skills")
    with st.expander("Add New Skill", expanded=False):
        with st.form("skill_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            skill_name = c1.text_input("Skill Name*")
            category = c2.selectbox("Category*", ["Technical", "Soft", "Language", "Tool"])
            proficiency = c3.slider("Proficiency (1-5)", 1, 5, 3)
            
            if st.form_submit_button("Add Skill"):
                if skill_name:
                    db_manager.add_skill({
                        "user_id": st.session_state.user_id, "skill_name": skill_name,
                        "category": category, "proficiency_level": proficiency
                    })
                    st.success("Skill Added!")
                    st.rerun()
    
    st.subheader("Your Skills")
    skills = db_manager.get_skills(st.session_state.user_id)
    for skill in skills:
        with st.container(border=True):
            st.markdown(f"**{skill['skill_name']}** (Category: {skill['category']})")
            if st.button("Delete", key=f"del_skill_{skill['id']}"):
                db_manager.delete_skill(skill['id'])
                st.rerun()

# Certifications Tab
with tab5:
    st.subheader("Add/Edit Certifications")
    with st.expander("Add New Certification", expanded=False):
        with st.form("cert_form", clear_on_submit=True):
            name = st.text_input("Certification Name*")
            org = st.text_input("Issuing Organization")
            issue_date = st.date_input("Issue Date", date(2021, 1, 1))
            
            if st.form_submit_button("Add Certification"):
                if name:
                    db_manager.add_certification({
                        "user_id": st.session_state.user_id, "name": name,
                        "issuing_organization": org, "issue_date": str(issue_date)
                    })
                    st.success("Certification Added!")
                    st.rerun()

    st.subheader("Your Certifications")
    certs = db_manager.get_certifications(st.session_state.user_id)
    for cert in certs:
        with st.container(border=True):
            st.markdown(f"**{cert['name']}** from **{cert['issuing_organization']}**")
            if st.button("Delete", key=f"del_cert_{cert['id']}"):
                db_manager.delete_certification(cert['id'])
                st.rerun()
