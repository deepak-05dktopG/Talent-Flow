import requests
import json
import re
from typing import Dict, List, Any, Optional
from app import config

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.1-8b-instant"

def clean_text(text: str) -> str:
    return re.sub(r'[^a-zA-Z0-9\s]', '', text)

def parse_json_from_text(text: str) -> Optional[Any]:
    list_start = text.find('[')
    list_end = text.rfind(']')
    dict_start = text.find('{')
    dict_end = text.rfind('}')
    
    if dict_start != -1 and (list_start == -1 or dict_start < list_start):
        try:
            return json.loads(text[dict_start:dict_end+1])
        except Exception:
            pass
    if list_start != -1:
        try:
            return json.loads(text[list_start:list_end+1])
        except Exception:
            pass
    if dict_start != -1:
        try:
            return json.loads(text[dict_start:dict_end+1])
        except Exception:
            pass
    try:
        clean = re.sub(r'```json\s*|\s*```', '', text).strip()
        return json.loads(clean)
    except Exception:
        return None

def _call_groq(prompt: str, system_prompt: str = "You are a helpful HR AI assistant.") -> Optional[str]:
    if not config.GROQ_API_KEY:
        print("Groq API key not set. Using local fallback.")
        return None
    
    headers = {
        "Authorization": f"Bearer {config.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 1024
    }
    
    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=12.0)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            print(f"Groq API Error (Status {response.status_code}): {response.text}")
    except Exception as e:
        print(f"Failed to contact Groq API: {e}")
    return None

def generate_resume_summary(parsed_info: Dict[str, Any]) -> str:
    prompt = f"""
    Create a professional, concise 2-sentence summary for the candidate based on these details:
    Name: {parsed_info.get('name')}
    Skills: {', '.join(parsed_info.get('skills', []))}
    Experience: {parsed_info.get('experience')}
    Education: {parsed_info.get('education')}
    """
    
    system_prompt = "You are an expert recruitment assistant. Generate a highly polished, two-sentence candidate profile summary."
    response = _call_groq(prompt, system_prompt)
    if response:
        return response
        
    # Heuristic Fallback
    skills = parsed_info.get("skills", [])
    exp = parsed_info.get("experience", "Not specified")
    edu = parsed_info.get("education", "Not specified")
    name = parsed_info.get("name", "The candidate")
    
    skills_str = ", ".join(skills[:5]) if skills else "various technologies"
    summary = f"Experienced professional with background in {skills_str}. Has experience described as '{exp}' and education from '{edu[:60]}'."
    return summary

def score_and_match_candidate(parsed_info: Dict[str, Any], job_desc: str, required_skills: List[str]) -> Dict[str, Any]:
    # Clean required skills to lowercase
    req_skills_lower = [s.lower() for s in required_skills]
    cand_skills_lower = [s.lower() for s in parsed_info.get("skills", [])]
    
    prompt = f"""
    Analyze the candidate's resume against the Job Description and Required Skills list.
    
    Candidate Skills: {', '.join(parsed_info.get('skills', []))}
    Candidate Experience: {parsed_info.get('experience')}
    Candidate Education: {parsed_info.get('education')}
    
    Required Job Skills: {', '.join(required_skills)}
    Job Description:
    {job_desc}
    
    Respond STRICTLY in JSON format with fields:
    - match_score: (an integer between 0 and 100 representing how well the candidate fits the requirements)
    - match_explanation: (2-sentence description of the fit criteria and justification for the score)
    - strengths: (list of up to 4 key skills or attributes that make the candidate a strong match)
    - missing_skills: (list of required skills or J.D. requirements the candidate is missing)
    - career_path: (list of 2 suggested roles for this candidate, e.g. ["Backend Developer", "DevOps Engineer"])
    """
    
    system_prompt = "You are a recruitment screening bot. You return only valid JSON parsing matches."
    response = _call_groq(prompt, system_prompt)
    
    if response:
        data = parse_json_from_text(response)
        if data and isinstance(data, dict):
            # Validate essential fields
            if "match_score" in data and "match_explanation" in data:
                return {
                    "match_score": int(data["match_score"]),
                    "match_explanation": data["match_explanation"],
                    "strengths": data.get("strengths", []),
                    "missing_skills": data.get("missing_skills", []),
                    "career_path": data.get("career_path", [])
                }
            
    # Algorithm Local Fallback: Heuristic Match Scoring
    matching_skills = []
    missing_skills = []
    
    for req in required_skills:
        req_clean = req.lower()
        matched = False
        # direct substring matching
        for skill in cand_skills_lower:
            if req_clean in skill or skill in req_clean:
                matching_skills.append(req)
                matched = True
                break
        if not matched:
            missing_skills.append(req)
            
    # Count skills match
    total_req = len(required_skills)
    skill_score_ratio = len(matching_skills) / max(total_req, 1)
    
    # Calculate score
    base_score = int(skill_score_ratio * 70) # 70% from matching skills
    
    # Experience score add (up to 30%)
    experience_text = str(parsed_info.get("experience", "")).lower()
    exp_bonus = 0
    # Search for numbers of years, e.g. "3 years", "5+", etc.
    year_match = re.search(r'(\d+)\s*year', experience_text)
    if year_match:
        years = int(year_match.group(1))
        if years >= 5:
            exp_bonus = 30
        elif years >= 3:
            exp_bonus = 25
        elif years >= 1:
            exp_bonus = 15
        else:
            exp_bonus = 5
    else:
        # Default bonus if experience contains words like 'experienced', 'senior'
        if "senior" in experience_text or "lead" in experience_text:
            exp_bonus = 25
        elif "developer" in experience_text or "engineer" in experience_text:
            exp_bonus = 15
        else:
            exp_bonus = 10
            
    match_score = min(base_score + exp_bonus, 100)
    
    # Heuristics explanation
    explanation = f"Matched {len(matching_skills)} out of {total_req} required skills. Experience keywords alignment is estimated at {exp_bonus}%."
    
    # Strengths
    strengths = [s.title() for s in matching_skills[:4]]
    if not strengths:
        strengths = [s.title() for s in parsed_info.get("skills", [])[:3]]
        if not strengths:
            strengths = ["Strong educational background" if parsed_info.get("education") else "General Tech Skills"]
            
    # missing skills
    missing = [s.title() for s in missing_skills[:4]]
    
    # Career recommendations
    c_path = []
    text_lower = (clean_text(str(parsed_info.get("raw_text", ""))).lower())
    if "react" in text_lower or "frontend" in text_lower or "html" in text_lower:
        c_path.append("Frontend Developer")
    if "python" in text_lower or "fastapi" in text_lower or "backend" in text_lower or "node" in text_lower:
        c_path.append("Backend Developer")
    if len(c_path) < 2:
        c_path.append("Full Stack Developer" if "developer" in text_lower or "engineer" in text_lower else "Software Engineer")
        
    return {
        "match_score": match_score,
        "match_explanation": explanation,
        "strengths": strengths,
        "missing_skills": missing,
        "career_path": c_path
    }

def generate_interview_questions(parsed_info: Dict[str, Any], difficulty: str) -> List[str]:
    prompt = f"""
    Generate 4 technical interview questions for a candidate with these details:
    Skills: {', '.join(parsed_info.get('skills', []))}
    Experience: {parsed_info.get('experience')}
    Education: {parsed_info.get('education')}
    
    Difficulty Level: {difficulty} (Easy, Medium, or Hard)
    
    Respond in JSON format as a list of strings:
    ["Question 1", "Question 2", "Question 3", "Question 4"]
    """
    
    system_prompt = "You are a technical interviewer. Return only a valid JSON array of strings."
    response = _call_groq(prompt, system_prompt)
    if response:
        questions = parse_json_from_text(response)
        if questions and isinstance(questions, list):
            return [str(q) for q in questions[:4]]
            
    # Fallback questions based on skills & difficulty
    skills = parsed_info.get("skills", [])
    diff_lower = difficulty.lower()
    
    skill_context = skills[0] if skills else "Software Engineering"
    
    if diff_lower == "easy":
        return [
            f"Explain the core components and architecture of a project you built using {skill_context}.",
            f"What are the main differences between relational databases and NoSQL databases?",
            f"What is your preferred programming language and why do you choose it?",
            f"Can you describe your role and contributions in your most recent project?"
        ]
    elif diff_lower == "hard":
        return [
            f"Design a highly scalable, distributed system using {skill_context}. How would you manage caching and race conditions?",
            f"How do you profile python/javascript code to identify memory leaks and database query bottlenecks?",
            f"Explain your strategy for securing APIs, preventing SQL injections, XSS, and handling secure file uploads.",
            f"How do you handle microservices database consistency using the Saga or Outbox pattern?"
        ]
    else: # Medium
        return [
            f"How do you handle asynchronous operations and error management in {skill_context} applications?",
            f"Describe a challenging technical problem you solved in your projects, and how you arrived at the solution.",
            f"What is your testing strategy (unit, integration, E2E) and which tools do you prefer for testing backend code?",
            f"What are REST best practices and how do you design versioned and secure APIs?"
        ]

def run_copilot_query(query: str, candidates: List[Dict[str, Any]], jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    import re
    query_lower = query.lower()
    
    # 1. Groq LLM Copilot Call (If Key is present)
    if config.GROQ_API_KEY:
        # Simplify candidate/job entries to pass to prompt within context limits
        compact_candidates = []
        for cand in candidates:
            compact_candidates.append({
                "name": cand.get("name"),
                "email": cand.get("email"),
                "skills": cand.get("parsed_skills", []),
                "match_score": cand.get("match_score", 0),
                "experience": cand.get("parsed_experience", ""),
                "status": cand.get("status", ""),
                "job_title": cand.get("job_title", "")
            })
            
        compact_jobs = []
        for job in jobs:
            compact_jobs.append({
                "title": job.get("title"),
                "skills": job.get("required_skills", []),
                "id": job.get("_id")
            })
            
        prompt = f"""
        User HR Query: "{query}"
        
        Candidates Pool:
        {json.dumps(compact_candidates, indent=1)}
        
        Jobs:
        {json.dumps(compact_jobs, indent=1)}
        
        Answer the HR query based on the data. Provide the response strictly in JSON format with fields:
        - natural_response: (1-3 sentences readable narrative answer)
        - suggested_action: (Optional action indicator, e.g. "filter", "compare", "interview", "questions" or null)
        - data: (list of filtered candidates that match the query, or an array of compared candidates)
        """
        system_prompt = "You are HR AI Copilot. Return only a valid JSON object with natural_response, suggested_action, and data fields."
        response = _call_groq(prompt, system_prompt)
        
        if response:
            ans = parse_json_from_text(response)
            if ans and isinstance(ans, dict) and "natural_response" in ans:
                return ans
                
    # 2. Heuristic Local Copilot Engine (Zero-Config Fallback)
    
    # "Show candidates with X" or "Which candidates are missing Y"
    skill_filter_pattern = re.search(r'(?:with|missing|have|know|knows)\s+([a-zA-Z\+\#\s\.\,\-\_]+)', query_lower)
    
    # Check if query is looking for missing skill: "missing X"
    is_missing_query = "missing" in query_lower or "don't have" in query_lower or "without" in query_lower
    
    # Filter candidates by skill
    if skill_filter_pattern:
        searched_skill = skill_filter_pattern.group(1).strip()
        # handle multiple separated skills
        skills_searched = [s.strip().replace(",", "").replace(".", "") for s in re.split(r'\s+and\s+|\s+or\s+|\,\s*', searched_skill) if s.strip()]
        
        matched_candidates = []
        for cand in candidates:
            cand_skills = [s.lower() for s in cand.get("parsed_skills", [])]
            
            # Check if matching
            has_match = False
            for s in skills_searched:
                s_lower = s.lower()
                # Check match
                any_skill_has = any(s_lower in c_s or c_s in s_lower for c_s in cand_skills)
                if any_skill_has:
                    has_match = True
                    break
                    
            if is_missing_query:
                # We want candidates that do NOT have the skill
                if not has_match:
                    matched_candidates.append(cand)
            else:
                if has_match:
                    matched_candidates.append(cand)
                    
        skills_str = " and ".join(skills_searched).title()
        if is_missing_query:
            natural = f"Found {len(matched_candidates)} candidate(s) who do not have {skills_str} in their profile."
        else:
            natural = f"Found {len(matched_candidates)} candidate(s) with skills matching {skills_str}."
            
        return {
            "natural_response": natural,
            "suggested_action": "filter",
            "data": matched_candidates
        }
        
    # "Who is the best candidate?"
    if "best" in query_lower or "top" in query_lower or "highest" in query_lower:
        sorted_cands = sorted(candidates, key=lambda x: x.get("match_score", 0), reverse=True)
        top_cands = sorted_cands[:3] # top 3
        
        if top_cands:
            names = [c.get("name") for c in top_cands]
            natural = f"The top candidate is {top_cands[0].get('name')} with a score of {top_cands[0].get('match_score')}/100, followed by {', '.join(names[1:])}."
        else:
            natural = "No candidates are currently available in the database to rank."
            
        return {
            "natural_response": natural,
            "suggested_action": "filter",
            "data": top_cands
        }
        
    # "Compare Deepak and Rahul"
    compare_pattern = re.findall(r'\b([a-zA-Z]{3,})\b', query)
    # Filter potential names
    names_to_compare = []
    for word in compare_pattern:
        if word.lower() not in ["compare", "who", "best", "candidate", "and", "show", "missing", "python", "docker", "fastapi"]:
            # Check if this matches a candidate name
            for cand in candidates:
                if word.lower() in cand.get("name", "").lower():
                    names_to_compare.append(cand)
                    break
                    
    # Remove duplicates from names_to_compare
    seen_ids = set()
    unique_comparisons = []
    for cand in names_to_compare:
        if cand["_id"] not in seen_ids:
            seen_ids.add(cand["_id"])
            unique_comparisons.append(cand)
            
    if len(unique_comparisons) >= 2:
        c1, c2 = unique_comparisons[0], unique_comparisons[1]
        natural = (f"Comparing {c1['name']} (Score: {c1['match_score']}/100) and "
                   f"{c2['name']} (Score: {c2['match_score']}/100). "
                   f"{c1['name']}'s main skills: {', '.join(c1['parsed_skills'][:4])}. "
                   f"{c2['name']}'s main skills: {', '.join(c2['parsed_skills'][:4])}.")
        return {
            "natural_response": natural,
            "suggested_action": "compare",
            "data": [c1, c2]
        }
        
    # Generate interview questions for the top candidate
    if "question" in query_lower or "interview questions" in query_lower:
        sorted_cands = sorted(candidates, key=lambda x: x.get("match_score", 0), reverse=True)
        if sorted_cands:
            top_cand = sorted_cands[0]
            questions = [
                f"How would you apply your skills in {', '.join(top_cand.get('parsed_skills', [])[:3])} to solve product engineering problems?",
                f"Describe a project from your experience (e.g. {top_cand.get('parsed_experience', '')[:100]}...) that was technically challenging.",
                "How do you design REST APIs and secure web application backends?",
                "What is your approach to automated testing and continuous integration?"
            ]
            natural = f"Generated interview questions for top candidate {top_cand['name']} based on their profile."
            # Pack questions into data
            return {
                "natural_response": natural,
                "suggested_action": "questions",
                "data": [{"candidate_name": top_cand["name"], "questions": questions}]
            }
        else:
            natural = "Could not find any candidates to generate questions for."
            return {
                "natural_response": natural,
                "suggested_action": None,
                "data": []
            }

    # Default response
    natural = "I can help search, rank, compare candidates, or list missing skills. Try queries like: 'Show candidates with Python' or 'Who is the best candidate?'"
    return {
        "natural_response": natural,
        "suggested_action": None,
        "data": []
    }
