import streamlit as st
from supabase import create_client
import groq

# Page config
st.set_page_config(
    page_title="AI Resume Tailor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

# Initialize clients
@st.cache_resource
def init_clients():
    try:
        supabase = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )
        groq_client = groq.Groq(api_key=st.secrets["GROQ_API_KEY"])
        return supabase, groq_client
    except Exception as e:
        st.error(f"Failed to initialize clients: {str(e)}")
        return None, None

# Main page
st.title("🚀 AI Resume Tailor")
st.markdown("### Generate ATS-optimized resumes tailored to each job application")

# Hero section
col1, col2, col3 = st.columns(3)

with col1:
    st.info("📋 **Step 1**\n\nSet up your profile with all your experiences, projects, and skills")

with col2:
    st.success("🎯 **Step 2**\n\nPaste a job description and let AI analyze it")

with col3:
    st.warning("📄 **Step 3**\n\nGet a perfectly tailored resume in seconds")

st.divider()

# Check if user is logged in
if st.session_state.user_id:
    st.success(f"✅ Logged in as: {st.session_state.user_email}")
    
    # Quick stats
    supabase, _ = init_clients()
    if supabase:
        col1, col2, col3, col4 = st.columns(4)
        
        # Get counts
        experiences = supabase.table('work_experiences').select("id").eq('user_id', st.session_state.user_id).execute()
        projects = supabase.table('projects').select("id").eq('user_id', st.session_state.user_id).execute()
        skills = supabase.table('skills').select("id").eq('user_id', st.session_state.user_id).execute()
        resumes = supabase.table('generated_resumes').select("id").eq('user_id', st.session_state.user_id).execute()
        
        with col1:
            st.metric("Work Experiences", len(experiences.data) if experiences.data else 0)
        with col2:
            st.metric("Projects", len(projects.data) if projects.data else 0)
        with col3:
            st.metric("Skills", len(skills.data) if skills.data else 0)
        with col4:
            st.metric("Resumes Generated", len(resumes.data) if resumes.data else 0)
else:
    st.warning("👈 Please set up your profile first using the sidebar")
    
    # Login section
    st.subheader("🔐 Login or Create Account")
    email = st.text_input("Enter your email address")
    
    if email and st.button("Continue"):
        supabase, _ = init_clients()
        if supabase:
            # Check if user exists
            existing_user = supabase.table('user_profiles').select("*").eq('email', email).execute()
            
            if existing_user.data:
                st.session_state.user_id = existing_user.data[0]['id']
                st.session_state.user_email = email
                st.success("Welcome back! Redirecting to your profile...")
                st.rerun()
            else:
                st.info("New user detected! Redirecting to profile setup...")
                st.session_state.user_email = email
                st.switch_page("pages/1_📋_Profile_Setup.py")

# Features section
st.divider()
st.subheader("✨ Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **🤖 AI-Powered Analysis**
    - Intelligent JD parsing
    - Skill matching
    - Keyword optimization
    
    **📊 Smart Selection**
    - Relevant experience selection
    - Project prioritization
    - Skill highlighting
    """)

with col2:
    st.markdown("""
    **📄 Professional Output**
    - ATS-friendly format
    - Clean, modern design
    - PDF export
    
    **☁️ Cloud-Based**
    - Access anywhere
    - Secure storage
    - Version history
    """)

# Footer
st.divider()
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit, LangGraph, and Groq")
