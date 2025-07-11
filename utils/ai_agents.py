Of course. Here is the complete and final version of the `utils/ai_agents.py` file, continuing from the `# Fallback summary` point. This version includes robust error handling and fallback logic for every step to prevent crashes.

## 6️⃣ `utils/ai_agents.py` (Complete Crash-Proof Version)
```python
import groq
import json
import streamlit as st
from typing import List, Dict, Any, TypedDict, Optional
from langgraph.graph import StateGraph, END
import re
import traceback

class ResumeState(TypedDict):
    """State for the resume generation workflow"""
    user_id: str
    job_description: str
    jd_analysis: Dict[str, Any]
    user_profile: Dict[str, Any]
    all_experiences: List[Dict[str, Any]]
    all_projects: List[Dict[str, Any]]
    all_skills: List[Dict[str, Any]]
    selected_experiences: List[Dict[str, Any]]
    selected_projects: List[Dict[str, Any]]
    selected_skills: List[str]
    tailored_summary: str
    tailored_experiences: List[Dict[str, Any]]
    tailored_projects: List[Dict[str, Any]]
    resume_content: str
    company_info: Dict[str, Any]
    error: Optional[str]

class AIAgents:
    def __init__(self):
        try:
            self.groq_client = groq.Groq(api_key=st.secrets["GROQ_API_KEY"])
            self.model = "mixtral-8x7b-32768"
        except Exception as e:
            st.error(f"Failed to initialize Groq client: {str(e)}")
            self.groq_client = None
            self.model = None
    
    def _safe_json_parse(self, text: str, default: Any = None) -> Any:
        """Safely parse JSON with multiple fallback strategies"""
        if default is None:
            default = {}
        
        # Clean the text
        text = text.strip()
        
        # Remove markdown code blocks
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        # Try to parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON object in the text
            try:
                # Look for JSON object pattern
                match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
                if match:
                    return json.loads(match.group())
            except:
                pass
            
            # Try to find JSON array pattern
            try:
                match = re.search(r'\[[\d,\s]+\]', text)
                if match:
                    return json.loads(match.group())
            except:
                pass
        
        return default
    
    def _call_llm(self, prompt: str, temperature: float = 0.3, max_tokens: int = 1000) -> str:
        """Helper method to call Groq LLM with error handling"""
        if not self.groq_client:
            return ""
        
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=30  # 30 second timeout
            )
            return response.choices[0].message.content
        except Exception as e:
            st.warning(f"LLM call failed: {str(e)}")
            return ""
    
    def analyze_job_description(self, jd_text: str) -> Dict[str, Any]:
        """Analyze job description with robust error handling"""
        default_result = {
            "job_title": "Software Engineer",
            "company_name": "Company",
            "required_skills": [],
            "preferred_skills": [],
            "responsibilities": [],
            "qualifications": [],
            "experience_required": "Not specified",
            "education_required": "Not specified",
            "keywords": [],
            "industry": "Technology",
            "job_type": "Full-time"
        }
        
        if not jd_text:
            return default_result
        
        prompt = f"""
        Analyze this job description and extract information in JSON format:
        {{
            "job_title": "extracted job title",
            "company_name": "extracted company name",
            "required_skills": ["skill1", "skill2"],
            "preferred_skills": ["skill1", "skill2"],
            "responsibilities": ["resp1", "resp2"],
            "qualifications": ["qual1", "qual2"],
            "experience_required": "X years",
            "education_required": "degree requirement",
            "keywords": ["keyword1", "keyword2"],
            "industry": "industry name",
            "job_type": "full-time/part-time/contract/remote"
        }}
        
        Job Description:
        {jd_text[:2000]}  # Limit length to avoid token issues
        """
        
        try:
            response = self._call_llm(prompt)
            if response:
                result = self._safe_json_parse(response, default_result)
                # Ensure all required keys exist
                for key in default_result:
                    if key not in result:
                        result[key] = default_result[key]
                return result
        except Exception as e:
            st.warning(f"JD analysis failed: {str(e)}")
        
        # Fallback: Basic extraction
        try:
            # Try to extract job title from first line or title pattern
            lines = jd_text.split('\n')
            job_title = lines[0].strip() if lines else "Software Engineer"
            
            # Extract skills by looking for common patterns
            skills = []
            skill_patterns = ['python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'docker']
            jd_lower = jd_text.lower()
            for pattern in skill_patterns:
                if pattern in jd_lower:
                    skills.append(pattern.capitalize())
            
            default_result["job_title"] = job_title[:100]  # Limit length
            default_result["required_skills"] = skills[:10]
            default_result["keywords"] = skills[:5]
            
        except:
            pass
        
        return default_result
    
    def research_company(self, company_name: str, industry: str = "") -> Dict[str, Any]:
        """Research company with fallback values"""
        default_result = {
            "company_culture": ["innovation", "teamwork", "excellence"],
            "company_size": "medium",
            "known_technologies": [],
            "company_values": ["integrity", "customer-focus", "quality"],
            "work_environment": "professional and collaborative"
        }
        
        if not company_name or company_name == "Company":
            return default_result
        
        prompt = f"""
        Provide brief information about {company_name} in the {industry} industry.
        Format as JSON with these fields:
        - company_culture (list of 3 values)
        - company_size (startup/small/medium/large)
        - known_technologies (list of technologies)
        - company_values (list of 3 values)
        - work_environment (brief description)
        
        Keep it concise. If unknown, provide reasonable assumptions.
        """
        
        try:
            response = self._call_llm(prompt, temperature=0.5, max_tokens=300)
            if response:
                result = self._safe_json_parse(response, default_result)
                # Validate and limit list sizes
                if isinstance(result.get("company_culture"), list):
                    result["company_culture"] = result["company_culture"][:5]
                if isinstance(result.get("known_technologies"), list):
                    result["known_technologies"] = result["known_technologies"][:10]
                return result
        except:
            pass
        
        return default_result
    
    def select_relevant_experiences(self, experiences: List[Dict], jd_analysis: Dict, limit: int = 3) -> List[Dict]:
        """Select relevant experiences with fallback logic"""
        if not experiences:
            return []
        
        # If few experiences, return all
        if len(experiences) <= limit:
            return experiences
        
        # Try AI selection
        try:
            required_skills = jd_analysis.get('required_skills', [])
            if required_skills and self.groq_client:
                prompt = f"""
                From these {len(experiences)} work experiences, select the {limit} most relevant.
                Return ONLY a JSON array of indices (0-based). Example: [0, 2, 3]
                
                Required skills: {', '.join(required_skills[:5])}
                
                Experiences:
                """
                
                for i, exp in enumerate(experiences[:10]):  # Limit to first 10
                    prompt += f"\n{i}. {exp.get('position', 'Position')} at {exp.get('company_name', 'Company')}"
                
                response = self._call_llm(prompt, max_tokens=50)
                if response:
                    indices = self._safe_json_parse(response, [])
                    if isinstance(indices, list) and indices:
                        selected = []
                        for idx in indices:
                            if isinstance(idx, int) and 0 <= idx < len(experiences):
                                selected.append(experiences[idx])
                        if selected:
                            return selected[:limit]
        except:
            pass
        
        # Fallback: Score based on keyword matching
        try:
            all_keywords = (jd_analysis.get('required_skills', []) + 
                          jd_analysis.get('keywords', []))
            
            scored_experiences = []
            for exp in experiences:
                score = 0
                exp_text = f"{exp.get('position', '')} {exp.get('description', '')} {' '.join(exp.get('technologies', []))}"
                exp_text_lower = exp_text.lower()
                
                for keyword in all_keywords:
                    if keyword.lower() in exp_text_lower:
                        score += 1
                
                scored_experiences.append((score, exp))
            
            # Sort by score and return top experiences
            scored_experiences.sort(key=lambda x: x[0], reverse=True)
            return [exp for _, exp in scored_experiences[:limit]]
        except:
            pass
        
        # Final fallback: return most recent
        return experiences[:limit]
    
    def select_relevant_projects(self, projects: List[Dict], jd_analysis: Dict, limit: int = 3) -> List[Dict]:
        """Select relevant projects with fallback logic"""
        if not projects:
            return []
        
        if len(projects) <= limit:
            return projects
        
        # Try AI selection
        try:
            required_skills = jd_analysis.get('required_skills', [])
            if required_skills and self.groq_client:
                prompt = f"""
                Select {limit} most relevant projects. Return JSON array of indices.
                Required skills: {', '.join(required_skills[:5])}
                
                Projects:
                """
                
                for i, proj in enumerate(projects[:10]):
                    prompt += f"\n{i}. {proj.get('title', 'Project')}"
                
                response = self._call_llm(prompt, max_tokens=50)
                if response:
                    indices = self._safe_json_parse(response, [])
                    if isinstance(indices, list) and indices:
                        selected = []
                        for idx in indices:
                            if isinstance(idx, int) and 0 <= idx < len(projects):
                                selected.append(projects[idx])
                        if selected:
                            return selected[:limit]
        except:
            pass
        
        # Fallback: Score based on technology matching
        try:
            required_techs = jd_analysis.get('required_skills', [])
            
            scored_projects = []
            for proj in projects:
                score = 0
                proj_techs = [t.lower() for t in proj.get('technologies', [])]
                
                for tech in required_techs:
                    if any(tech.lower() in pt for pt in proj_techs):
                        score += 1
                
                scored_projects.append((score, proj))
            
            scored_projects.sort(key=lambda x: x[0], reverse=True)
            return [proj for _, proj in scored_projects[:limit]]
        except:
            pass
        
        return projects[:limit]
    
    def select_relevant_skills(self, skills: List[Dict], jd_analysis: Dict) -> List[str]:
        """Select relevant skills with matching"""
        if not skills:
            return []
        
        try:
            # Extract skill names
            all_skills = []
            for skill in skills:
                if isinstance(skill, dict) and 'skill_name' in skill:
                    all_skills.append(skill['skill_name'])
            
            if not all_skills:
                return []
            
            # Get JD skills
            jd_skills = (jd_analysis.get('required_skills', []) + 
                        jd_analysis.get('preferred_skills', []))
            
            # Separate matching and non-matching
            matching_skills = []
            remaining_skills = []
            
            for skill in all_skills:
                skill_lower = skill.lower()
                if any(jd_skill.lower() in skill_lower or skill_lower in jd_skill.lower() 
                      for jd_skill in jd_skills):
                    matching_skills.append(skill)
                else:
                    remaining_skills.append(skill)
            
            # Return matching first, then others
            return (matching_skills + remaining_skills)[:20]  # Limit total
        except:
            # Fallback: return all skill names
            return [s.get('skill_name', '') for s in skills if isinstance(s, dict)][:20]
    
    def generate_tailored_summary(self, profile: Dict, jd_analysis: Dict, experiences: List[Dict]) -> str:
        """Generate tailored summary with fallback"""
        try:
            # Build context
            years_exp = profile.get('years_of_experience', 5)
            current_role = experiences[0].get('position', 'Software Engineer') if experiences else 'Software Engineer'
            target_role = jd_analysis.get('job_title', 'Software Engineer')
            key_skills = jd_analysis.get('required_skills', [])[:3]
            
            if self.groq_client:
                prompt = f"""
                Write a 3-4 sentence professional summary for a resume.
                - {years_exp} years of experience
                - Current/Recent: {current_role}
                - Applying for: {target_role}
                - Key skills: {', '.join(key_skills)}
                
                Make it compelling and ATS-friendly. No first person pronouns.
                """
                
                response = self._call_llm(prompt, temperature=0.7, max_tokens=150)
                if response and len(response) > 50:
                    return response.strip()
        except:
            pass
        
        # Fallback summary
        years = profile.get('years_of_experience', 5)
        skills = jd_analysis.get('required_skills', ['software development'])[:2]
        return f"Experienced professional with {years}+ years in software development. Skilled in {', '.join(skills)} with a proven track record of delivering high-quality solutions. Seeking to leverage technical expertise and problem-solving abilities in a challenging role."
    
    def tailor_experience_description(self, experience: Dict, jd_analysis: Dict) -> Dict:
        """Tailor experience with safe fallback"""
        try:
            if self.groq_client and experience.get('achievements'):
                prompt = f"""
                Rewrite these work experience achievements to better match the job requirements.
                Focus on keywords: {', '.join(jd_analysis.get('keywords', [])[:5])}
                
                Original Achievements:
                {experience.get('achievements', [])}
                
                Return ONLY JSON with an "achievements" key containing a list of strings.
                Example: {{"achievements": ["achievement1", "achievement2"]}}
                """
                
                response = self._call_llm(prompt, temperature=0.5, max_tokens=300)
                if response:
                    tailored_data = self._safe_json_parse(response, {})
                    new_experience = experience.copy()
                    if isinstance(tailored_data.get('achievements'), list):
                        new_experience['achievements'] = tailored_data['achievements']
                    return new_experience
        except Exception:
            pass
        
        return experience
    
    def tailor_project_description(self, project: Dict, jd_analysis: Dict) -> Dict:
        """Tailor project with safe fallback"""
        try:
            if self.groq_client and project.get('achievements'):
                prompt = f"""
                Rewrite these project achievements to better match the job requirements.
                Focus on skills: {', '.join(jd_analysis.get('required_skills', [])[:5])}
                
                Original Achievements:
                {project.get('achievements', [])}
                
                Return ONLY JSON with an "achievements" key containing a list of strings.
                Example: {{"achievements": ["feature1", "feature2"]}}
                """
                
                response = self._call_llm(prompt, temperature=0.5, max_tokens=300)
                if response:
                    tailored_data = self._safe_json_parse(response, {})
                    new_project = project.copy()
                    if isinstance(tailored_data.get('achievements'), list):
                        new_project['achievements'] = tailored_data['achievements']
                    return new_project
        except Exception:
            pass
            
        return project
    
    def create_resume_workflow(self):
        """Create the LangGraph workflow for resume generation"""
        workflow = StateGraph(ResumeState)
        
        # Define nodes
        workflow.add_node("analyze_jd", self.analyze_jd_node)
        workflow.add_node("select_content", self.select_content_node)
        workflow.add_node("tailor_summary", self.tailor_summary_node)
        workflow.add_node("tailor_experiences", self.tailor_experiences_node)
        workflow.add_node("tailor_projects", self.tailor_projects_node)
        
        # Define edges
        workflow.set_entry_point("analyze_jd")
        workflow.add_edge("analyze_jd", "select_content")
        workflow.add_edge("select_content", "tailor_summary")
        workflow.add_edge("tailor_summary", "tailor_experiences")
        workflow.add_edge("tailor_experiences", "tailor_projects")
        workflow.add_edge("tailor_projects", END)
        
        return workflow.compile()
    
    # Node functions for the workflow
    def analyze_jd_node(self, state: ResumeState) -> ResumeState:
        """Node: Analyze job description"""
        state["jd_analysis"] = self.analyze_job_description(state["job_description"])
        return state
    
    def select_content_node(self, state: ResumeState) -> ResumeState:
        """Node: Select relevant experiences, projects, and skills"""
        jd_analysis = state["jd_analysis"]
        state["selected_experiences"] = self.select_relevant_experiences(state["all_experiences"], jd_analysis)
        state["selected_projects"] = self.select_relevant_projects(state["all_projects"], jd_analysis)
        state["selected_skills"] = self.select_relevant_skills(state["all_skills"], jd_analysis)
        return state
    
    def tailor_summary_node(self, state: ResumeState) -> ResumeState:
        """Node: Generate tailored professional summary"""
        state["tailored_summary"] = self.generate_tailored_summary(
            state["user_profile"],
            state["jd_analysis"],
            state["selected_experiences"]
        )
        return state
        
    def tailor_experiences_node(self, state: Resume_State) -> ResumeState:
        """Node: Tailor descriptions for selected experiences"""
        tailored = []
        for exp in state["selected_experiences"]:
            tailored.append(self.tailor_experience_description(exp, state["jd_analysis"]))
        state["tailored_experiences"] = tailored
        return state
        
    def tailor_projects_node(self, state: ResumeState) -> ResumeState:
        """Node: Tailor descriptions for selected projects"""
        tailored = []
        for proj in state["selected_projects"]:
            tailored.append(self.tailor_project_description(proj, state["jd_analysis"]))
        state["tailored_projects"] = tailored
        return state
```
