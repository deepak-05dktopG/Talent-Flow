import re
import os
from typing import Dict, List, Any
import PyPDF2
import docx

# A rich, standard skill taxonomy to search for in candidate resumes:
SKILLS_TAXONOMY = [
    "python", "javascript", "typescript", "java", "c++", "c#", "ruby", "golang", "rust", "php", "swift",
    "react", "angular", "vue", "next.js", "node.js", "express", "django", "flask", "fastapi", "spring boot",
    "html", "css", "bootstrap", "tailwind", "jquery",
    "mongodb", "postgresql", "mysql", "redis", "cassandra", "sqlite", "oracle", "database",
    "docker", "kubernetes", "aws", "azure", "gcp", "devops", "ci/cd", "git", "jenkins", "terraform",
    "machine learning", "deep learning", "nlp", "tensorflow", "pytorch", "spacy", "scikit-learn",
    "project management", "agile", "scrum", "product management", "jira",
    "data science", "data analysis", "tableau", "power bi", "pandas", "numpy",
    "rest api", "graphql", "grpc", "microservices", "serverless",
    "communication", "leadership", "problem solving", "teamwork", "analytical skills"
]

def extract_text_from_pdf(filepath: str) -> str:
    text = ""
    try:
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"Error reading PDF {filepath}: {e}")
    return text

def extract_text_from_docx(filepath: str) -> str:
    text = []
    try:
        doc = docx.Document(filepath)
        for para in doc.paragraphs:
            text.append(para.text)
    except Exception as e:
        print(f"Error reading DOCX {filepath}: {e}")
    return "\n".join(text)

def extract_text_from_txt(filepath: str) -> str:
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading TXT {filepath}: {e}")
        return ""

def extract_text(filepath: str) -> str:
    _, ext = os.path.splitext(filepath.lower())
    if ext == ".pdf":
        return extract_text_from_pdf(filepath)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(filepath)
    elif ext == ".txt":
        return extract_text_from_txt(filepath)
    return ""

def clean_text(text: str) -> str:
    # normalize spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_resume(filepath: str) -> Dict[str, Any]:
    text = extract_text(filepath)
    clean_txt = clean_text(text)
    
    # 1. Extract Email
    email = ""
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', clean_txt)
    if email_match:
        email = email_match.group(0)

    # 2. Extract Phone Number
    phone = ""
    # Matches patterns like +1 (234) 567-8901, 0987654321, etc.
    phone_match = re.search(r'(\+?\d{1,4}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', clean_txt)
    if phone_match:
        phone = phone_match.group(0)

    # 3. Extract Name
    # Fallback to first line of text or email username if name extraction fails
    name = ""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if lines:
        # Avoid common titles like 'Resume', 'Curriculum Vitae', etc.
        ignored_names = ["resume", "cv", "curriculum vitae", "profile", "contact", "summary"]
        for line in lines[:3]: # check first 3 lines
            if line.lower() not in ignored_names and len(line.split()) >= 2 and len(line.split()) <= 4:
                # Basic check for Name capitalized words
                if all(w[0].isupper() for w in line.split() if w.isalpha()):
                    name = line
                    break
        if not name:
            name = lines[0] # select first line
    
    if not name or len(name) > 50:
        # Fallback to email username if name is invalid
        if email:
            name = email.split("@")[0].replace(".", " ").title()
        else:
            name = "Candidate"

    # 4. Extract Skills
    skills = []
    # Search for skills in taxonomy case-insensitively
    text_lower = clean_txt.lower()
    for skill in SKILLS_TAXONOMY:
        # Use word boundaries so that 'c' does not match every word, or 'java' doesn't match 'javascript'
        # Escaping special characters in skill (like c++)
        escaped_skill = re.escape(skill)
        # Handle word boundary or special character boundaries:
        if "+" in skill or "#" in skill or "." in skill:
            pattern = rf'(?:^|[\s,.\-:;/])({escaped_skill})(?:$|[\s,.\-:;/])'
        else:
            pattern = rf'\b{escaped_skill}\b'
            
        if re.search(pattern, text_lower):
            skills.append(skill.title() if skill not in ["aws", "gcp", "ci/cd", "sql", "api", "rest api", "html", "css", "nlp", "jd"] else skill.upper())

    # 5. Extract Education
    education = ""
    edu_keywords = ["college", "university", "institute", "school", "academy", "degree", "bachelor", "master", "phd", "btech", "mtech", "b.tech", "m.tech", "bsc", "msc", "b.s", "m.s"]
    edu_lines = []
    for line in text.split("\n"):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in edu_keywords):
            edu_lines.append(line.strip())
    if edu_lines:
        education = " | ".join(edu_lines[:3]) # Limit to top 3 matching education entries
    else:
        education = "Not clearly specified"

    # 6. Extract Experience
    experience = ""
    exp_keywords = ["experience", "work history", "employment", "internship", "professional background", "job title", "developer", "engineer", "manager"]
    exp_lines = []
    # Also look for years of experience pattern (e.g. "3 years of experience", "2+ years")
    years_match = re.search(r'(\d+\+?\s*(?:years|yrs)?\s*(?:of)?\s*experience)', clean_txt, re.IGNORECASE)
    
    for line in text.split("\n"):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in exp_keywords):
            # Avoid matching skills list section lines
            if "skills" not in line_lower and len(line.strip()) > 10 and len(line.strip()) < 150:
                exp_lines.append(line.strip())
    if exp_lines:
        experience = " | ".join(exp_lines[:3])
        if years_match:
            experience = f"{years_match.group(0)} - {experience}"
    else:
        if years_match:
            experience = years_match.group(0)
        else:
            experience = "Not clearly specified"

    # 7. Extract LinkedIn & GitHub
    linkedin = ""
    linkedin_match = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_\-\/\?\&]+', clean_txt, re.IGNORECASE)
    if linkedin_match:
        linkedin = linkedin_match.group(0)

    github = ""
    github_match = re.search(r'(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_\-\/\?\&]+', clean_txt, re.IGNORECASE)
    if github_match:
        github = github_match.group(0)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "skills": list(set(skills)),
        "education": education,
        "experience": experience,
        "raw_text": text[:6000] # Store preview of first 6000 characters
    }
