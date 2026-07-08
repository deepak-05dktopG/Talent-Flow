"""
services/parser_service.py - Document Text Extractor & Resume Parser
======================================================================
This file handles reading uploaded files (PDFs, Word documents, text files)
and extracting the text content case-by-case, then parsing details from that text.

How it works:
1. Candidate uploads a resume file (.pdf, .docx, or .txt).
2. The service detects the file type and extracts raw text using:
   - PyPDF2 for PDF files (reads page contents)
   - docx library for Microsoft Word files (reads document paragraphs)
   - UTF-8 text reader for plain text files
3. Once raw text is extracted, we use regular expressions (advanced text matching)
   and a predefined list of skills (SKILLS_TAXONOMY) to pull out details:
   - Candidate Name
   - Email Address
   - Phone Number
   - Technical & Soft Skills
   - Education details (college names, degrees)
   - Work Experience (companies, years)
   - LinkedIn & GitHub profile links
"""

import re
import os
from typing import Dict, List, Any
import PyPDF2
import docx

# ──────────────────────────────────────────────
# SKILL TAXONOMY
# A curated dictionary of common industry terms to search for in candidate resumes.
# ──────────────────────────────────────────────
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
    """Reads page-by-page contents of a PDF file and joins them into a single string."""
    text = ""
    try:
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            # Loop through every page in the PDF and read its text
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"Error reading PDF {filepath}: {e}")
    return text

def extract_text_from_docx(filepath: str) -> str:
    """Reads all paragraphs in a Microsoft Word DOCX file and joins them with linebreaks."""
    text = []
    try:
        doc = docx.Document(filepath)
        # Extract text from every paragraph block in the document
        for para in doc.paragraphs:
            text.append(para.text)
    except Exception as e:
        print(f"Error reading DOCX {filepath}: {e}")
    return "\n".join(text)

def extract_text_from_txt(filepath: str) -> str:
    """Reads plain text files using UTF-8 encoding. Safely ignores any corrupt characters."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading TXT {filepath}: {e}")
        return ""

def extract_text(filepath: str) -> str:
    """
    Acts as a router: inspects the file extension
    and calls the correct text extraction function.
    """
    _, ext = os.path.splitext(filepath.lower())
    if ext == ".pdf":
        return extract_text_from_pdf(filepath)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(filepath)
    elif ext == ".txt":
        return extract_text_from_txt(filepath)
    return ""

def clean_text(text: str) -> str:
    """Replaces duplicate spaces, tabs, and newlines with a single space to make searching easier."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_resume(filepath: str) -> Dict[str, Any]:
    """
    Reads a resume file and extracts structured fields using regular expressions.
    
    Steps:
    1. Extract all raw text from the document.
    2. Extract email address using a standard email regex pattern.
    3. Extract phone number looking for standard 10-digit formats with prefixes.
    4. Guess the candidate's name by looking at the first 3 lines of capitalized words.
    5. Search for skills defined in SKILLS_TAXONOMY (using word boundaries to prevent false positives).
    6. Extract education sections matching terms like "University" or "Degree".
    7. Tally experience sections looking for terms like "Experience" or "years of experience".
    8. Find links targeting linkedin.com or github.com.
    """
    text = extract_text(filepath)
    clean_txt = clean_text(text)
    
    # 1. Extract Email — looks for text matching username@domain.extension
    email = ""
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', clean_txt)
    if email_match:
        email = email_match.group(0)

    # 2. Extract Phone Number — matches standard layouts like +1 234-567-8901, 1234567890
    phone = ""
    phone_match = re.search(r'(\+?\d{1,4}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', clean_txt)
    if phone_match:
        phone = phone_match.group(0)

    # 3. Extract Name
    # We inspect the top lines of the resume (where names are typically situated).
    name = ""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if lines:
        ignored_names = ["resume", "cv", "curriculum vitae", "profile", "contact", "summary"]
        for line in lines[:3]: # Check the first 3 lines
            # If the line looks like a typical name (2 to 4 capitalized words, no numbers)
            if line.lower() not in ignored_names and len(line.split()) >= 2 and len(line.split()) <= 4:
                if all(w[0].isupper() for w in line.split() if w.isalpha()):
                    name = line
                    break
        if not name:
            name = lines[0] # Select the first line as a fallback
    
    # If name extraction yields no result, fall back to email user name or "Candidate"
    if not name or len(name) > 50:
        if email:
            name = email.split("@")[0].replace(".", " ").title()
        else:
            name = "Candidate"

    # 4. Extract Skills
    # Search for skills defined in SKILLS_TAXONOMY case-insensitively.
    skills = []
    text_lower = clean_txt.lower()
    for skill in SKILLS_TAXONOMY:
        escaped_skill = re.escape(skill)
        # Use word boundary boundaries (\b) so "c" doesn't match every word
        if "+" in skill or "#" in skill or "." in skill:
            pattern = rf'(?:^|[\s,.\-:;/])({escaped_skill})(?:$|[\s,.\-:;/])'
        else:
            pattern = rf'\b{escaped_skill}\b'
            
        if re.search(pattern, text_lower):
            # Format display correctly (uppercase acronyms, titlecase other skills)
            skills.append(skill.title() if skill not in ["aws", "gcp", "ci/cd", "sql", "api", "rest api", "html", "css", "nlp", "jd"] else skill.upper())

    # 5. Extract Education
    # Look for lines containing academic terms like "university", "college", or degree names
    education = ""
    edu_keywords = ["college", "university", "institute", "school", "academy", "degree", "bachelor", "master", "phd", "btech", "mtech", "b.tech", "m.tech", "bsc", "msc", "b.s", "m.s"]
    edu_lines = []
    for line in text.split("\n"):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in edu_keywords):
            edu_lines.append(line.strip())
    if edu_lines:
        education = " | ".join(edu_lines[:3]) # Display top 3 entries
    else:
        education = "Not clearly specified"

    # 6. Extract Experience
    # Look for lines containing work keywords, and search for patterns like "5+ years of experience"
    experience = ""
    exp_keywords = ["experience", "work history", "employment", "internship", "professional background", "job title", "developer", "engineer", "manager"]
    exp_lines = []
    years_match = re.search(r'(\d+\+?\s*(?:years|yrs)?\s*(?:of)?\s*experience)', clean_txt, re.IGNORECASE)
    
    for line in text.split("\n"):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in exp_keywords):
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

    # 7. Extract LinkedIn & GitHub Links
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
        "skills": list(set(skills)),  # Remove duplicate skills
        "education": education,
        "experience": experience,
        "raw_text": text[:6000]        # Save preview of text for verification
    }
