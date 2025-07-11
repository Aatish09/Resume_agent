import markdown2
from weasyprint import HTML, CSS
from datetime import datetime
from typing import Dict, List, Any

class ResumeGenerator:
    def __init__(self):
        # ATS-friendly and professional CSS styling
        self.css_style = """
        @page {
            size: A4;
            margin: 1.5cm;
        }
        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.4;
            color: #333;
        }
        h1 {
            font-size: 24pt;
            font-weight: bold;
            margin: 0;
            padding: 0;
            text-align: center;
            color: #2c3e50;
        }
        h2 {
            font-size: 14pt;
            font-weight: bold;
            color: #34495e;
            border-bottom: 2px solid #34495e;
            padding-bottom: 4px;
            margin-top: 1cm;
            margin-bottom: 0.4cm;
        }
        h3 {
            font-size: 12pt;
            font-weight: bold;
            color: #2c3e50;
            margin: 0;
            padding: 0;
        }
        p, ul, li {
            margin: 0;
            padding: 0;
        }
        ul {
            list-style-type: none;
            padding-left: 0;
        }
        li {
            padding-left: 1.2em;
            position: relative;
        }
        li:before {
            content: '•';
            position: absolute;
            left: 0;
            top: 0;
            color: #34495e;
        }
        .contact-info {
            text-align: center;
            font-size: 10pt;
            margin-bottom: 0.8cm;
            color: #555;
        }
        .section {
            margin-bottom: 0.6cm;
        }
        .job, .project, .education-item {
            margin-bottom: 0.5cm;
        }
        .job-title-line, .project-title-line, .education-title-line {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
        }
        .job-title-line h3, .project-title-line h3, .education-title-line h3 {
            flex-grow: 1;
        }
        .date-location {
            font-style: italic;
            font-size: 10pt;
            color: #555;
            flex-shrink: 0;
        }
        .skills-category {
            margin-bottom: 0.2cm;
        }
        .skills-category strong {
            color: #2c3e50;
        }
        """

    def _generate_markdown(self, state: Dict[str, Any]) -> str:
        """Constructs the resume content as a Markdown string."""
        profile = state.get("user_profile", {})
        
        # Header
        contact_parts = [
            profile.get('location', ''),
            profile.get('phone', ''),
            profile.get('email', '')
        ]
        links_parts = [
            f"LinkedIn: {profile.get('linkedin_url', '')}" if profile.get('linkedin_url') else None,
            f"GitHub: {profile.get('github_url', '')}" if profile.get('github_url') else None,
            f"Portfolio: {profile.get('portfolio_url', '')}" if profile.get('portfolio_url') else None
        ]

        md = f"<h1>{profile.get('full_name', 'Your Name')}</h1>\n"
        md += f"<div class='contact-info'>\n"
        md += " | ".join(filter(None, contact_parts)) + "<br/>\n"
        md += " | ".join(filter(None, links_parts)) + "\n"
        md += f"</div>\n\n"

        # Summary
        md += "<h2>Professional Summary</h2>\n"
        md += f"<div class='section'><p>{state.get('tailored_summary', '')}</p></div>\n\n"

        # Work Experience
        if state.get("tailored_experiences"):
            md += "<h2>Work Experience</h2>\n"
            for exp in state["tailored_experiences"]:
                start_date = exp.get('start_date', 'N/A').split('-')[0]
                end_date = exp.get('end_date', 'Present').split('-')[0] if not exp.get('is_current') else 'Present'
                md += f"<div class='job'>\n"
                md += f"<div class='job-title-line'><h3>{exp.get('position', '')} at {exp.get('company_name', '')}</h3><span class='date-location'>{start_date} - {end_date} | {exp.get('location', '')}</span></div>\n"
                md += "<ul>\n"
                for achievement in exp.get('achievements', []):
                    md += f"<li>{achievement}</li>\n"
                md += "</ul>\n"
                if exp.get('technologies'):
                    md += f"<p><strong>Technologies:</strong> {', '.join(exp['technologies'])}</p>\n"
                md += "</div>\n"
            md += "\n"

        # Projects
        if state.get("tailored_projects"):
            md += "<h2>Projects</h2>\n"
            for proj in state["tailored_projects"]:
                md += f"<div class='project'>\n"
                md += f"<div class='project-title-line'><h3>{proj.get('title', '')}</h3></div>\n"
                md += "<ul>\n"
                for achievement in proj.get('achievements', []):
                    md += f"<li>{achievement}</li>\n"
                md += "</ul>\n"
                if proj.get('technologies'):
                    md += f"<p><strong>Technologies:</strong> {', '.join(proj['technologies'])}</p>\n"
                md += "</div>\n"
            md += "\n"

        # Skills
        if state.get("all_skills"):
            md += "<h2>Skills</h2>\n"
            skills_by_cat = {}
            for skill in state.get("all_skills", []):
                cat = skill.get('category', 'General').title()
                if cat not in skills_by_cat:
                    skills_by_cat[cat] = []
                skills_by_cat[cat].append(skill.get('skill_name'))
            
            for cat, skills_list in skills_by_cat.items():
                md += f"<div class='skills-category'><strong>{cat}:</strong> {', '.join(skills_list)}</div>\n"
            md += "\n"

        # Education
        education = state.get("user_profile", {}).get("education", [])
        if education:
            md += "<h2>Education</h2>\n"
            for edu in education:
                start_date = edu.get('start_date', 'N/A').split('-')[0]
                end_date = edu.get('end_date', 'N/A').split('-')[0]
                md += f"<div class='education-item'>\n"
                md += f"<div class='education-title-line'><h3>{edu.get('degree', '')} in {edu.get('field_of_study', '')}</h3><span class='date-location'>{start_date} - {end_date}</span></div>\n"
                md += f"<p>{edu.get('institution', '')}, {edu.get('location', '')}</p>\n"
                md += "</div>\n"
            md += "\n"

        return md

    def create_pdf(self, state: Dict[str, Any]) -> bytes:
        """Generates a PDF from the final state and returns its byte content."""
        markdown_content = self._generate_markdown(state)
        html_content = markdown2.markdown(markdown_content, extras=["tables"])
        
        css = CSS(string=self.css_style)
        pdf_bytes = HTML(string=html_content).write_pdf(stylesheets=[css])
        
        return pdf_bytes, markdown_content
