from supabase import create_client, Client
import streamlit as st
from typing import List, Dict, Any, Optional
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.supabase: Client = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )
    
    # User Profile Operations
    def create_user_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user profile"""
        response = self.supabase.table('user_profiles').insert(profile_data).execute()
        return response.data[0] if response.data else None
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile by ID"""
        response = self.supabase.table('user_profiles').select("*").eq('id', user_id).execute()
        return response.data[0] if response.data else None
    
    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        response = self.supabase.table('user_profiles').update(updates).eq('id', user_id).execute()
        return response.data[0] if response.data else None
    
    # Work Experience Operations
    def add_work_experience(self, experience_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add work experience"""
        response = self.supabase.table('work_experiences').insert(experience_data).execute()
        return response.data[0] if response.data else None
    
    def get_work_experiences(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all work experiences for a user"""
        response = self.supabase.table('work_experiences').select("*").eq('user_id', user_id).order('start_date', desc=True).execute()
        return response.data or []
    
    def update_work_experience(self, exp_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update work experience"""
        response = self.supabase.table('work_experiences').update(updates).eq('id', exp_id).execute()
        return response.data[0] if response.data else None
    
    def delete_work_experience(self, exp_id: str) -> bool:
        """Delete work experience"""
        response = self.supabase.table('work_experiences').delete().eq('id', exp_id).execute()
        return True
    
    # Project Operations
    def add_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add project"""
        response = self.supabase.table('projects').insert(project_data).execute()
        return response.data[0] if response.data else None
    
    def get_projects(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all projects for a user"""
        response = self.supabase.table('projects').select("*").eq('user_id', user_id).order('start_date', desc=True).execute()
        return response.data or []
    
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update project"""
        response = self.supabase.table('projects').update(updates).eq('id', project_id).execute()
        return response.data[0] if response.data else None
    
    def delete_project(self, project_id: str) -> bool:
        """Delete project"""
        response = self.supabase.table('projects').delete().eq('id', project_id).execute()
        return True
    
    # Education Operations
    def add_education(self, education_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add education"""
        response = self.supabase.table('education').insert(education_data).execute()
        return response.data[0] if response.data else None
    
    def get_education(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all education for a user"""
        response = self.supabase.table('education').select("*").eq('user_id', user_id).order('start_date', desc=True).execute()
        return response.data or []
    
    def delete_education(self, edu_id: str) -> bool:
        """Delete education"""
        response = self.supabase.table('education').delete().eq('id', edu_id).execute()
        return True
    
    # Skills Operations
    def add_skill(self, skill_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add skill"""
        response = self.supabase.table('skills').insert(skill_data).execute()
        return response.data[0] if response.data else None
    
    def get_skills(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all skills for a user"""
        response = self.supabase.table('skills').select("*").eq('user_id', user_id).order('proficiency_level', desc=True).execute()
        return response.data or []
    
    def get_skills_by_category(self, user_id: str, category: str) -> List[Dict[str, Any]]:
        """Get skills by category"""
        response = self.supabase.table('skills').select("*").eq('user_id', user_id).eq('category', category).execute()
        return response.data or []
    
    def delete_skill(self, skill_id: str) -> bool:
        """Delete skill"""
        response = self.supabase.table('skills').delete().eq('id', skill_id).execute()
        return True
    
    # Certifications Operations
    def add_certification(self, cert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add certification"""
        response = self.supabase.table('certifications').insert(cert_data).execute()
        return response.data[0] if response.data else None
    
    def get_certifications(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all certifications for a user"""
        response = self.supabase.table('certifications').select("*").eq('user_id', user_id).order('issue_date', desc=True).execute()
        return response.data or []
    
    def delete_certification(self, cert_id: str) -> bool:
        """Delete certification"""
        response = self.supabase.table('certifications').delete().eq('id', cert_id).execute()
        return True
    
    # Resume Operations
    def save_generated_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save generated resume"""
        response = self.supabase.table('generated_resumes').insert(resume_data).execute()
        return response.data[0] if response.data else None
    
    def get_generated_resumes(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all generated resumes for a user"""
        response = self.supabase.table('generated_resumes').select("*").eq('user_id', user_id).order('created_at', desc=True).execute()
        return response.data or []
    
    def get_resume_by_id(self, resume_id: str) -> Optional[Dict[str, Any]]:
        """Get specific resume by ID"""
        response = self.supabase.table('generated_resumes').select("*").eq('id', resume_id).execute()
        return response.data[0] if response.data else None
      
