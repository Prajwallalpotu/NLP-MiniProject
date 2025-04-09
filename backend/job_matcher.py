import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nlp_processor import preprocess_text, extract_keywords
from resume_parser import extract_skills
from google import genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def match_resume_with_job(resume_text, job_description):
    """
    Match a resume with a job description using a detailed analysis approach.
    
    Args:
        resume_text (str): Extracted text from the resume
        job_description (str): Job description text
        
    Returns:
        dict: Match results including score, strengths, weaknesses, and suggestions
    """
    try:
        # Extract structured sections from the resume
        resume_sections = extract_resume_sections(resume_text)
        
        # Extract key requirements from the job description
        job_requirements = extract_job_requirements(job_description)
        
        # Analyze each section of the resume against the job requirements
        analysis = {
            "experience_match": analyze_experience(resume_sections.get("experience", ""), job_requirements.get("experience", "")),
            "skills_match": analyze_skills(resume_sections.get("skills", ""), job_requirements.get("skills", "")),
            "education_match": analyze_education(resume_sections.get("education", ""), job_requirements.get("education", "")),
            "achievements_match": analyze_achievements(resume_sections.get("achievements", ""), job_requirements.get("achievements", ""))
        }
        
        # Calculate an overall match score
        overall_score = calculate_overall_score(analysis)
        
        # Generate strengths, weaknesses, and suggestions
        strengths = generate_strengths(analysis)
        weaknesses = generate_weaknesses(analysis)
        suggestions = generate_suggestions(analysis, job_requirements)
        
        return {
            "score": overall_score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggestions": suggestions
        }
    
    except Exception as e:
        # Fallback to TF-IDF based matching if detailed analysis fails
        return fallback_match_resume_with_job(resume_text, job_description)

def extract_resume_sections(resume_text):
    """
    Extract structured sections from the resume text.
    """
    # Implement logic to parse and extract sections like experience, skills, education, etc.
    # Example:
    return {
        "experience": "Extracted experience section",
        "skills": "Extracted skills section",
        "education": "Extracted education section",
        "achievements": "Extracted achievements section"
    }

def extract_job_requirements(job_description):
    """
    Extract key requirements from the job description.
    """
    # Implement logic to parse and extract requirements like required skills, experience, etc.
    # Example:
    return {
        "experience": "Required experience details",
        "skills": "Required skills",
        "education": "Required education",
        "achievements": "Preferred achievements"
    }

def analyze_experience(resume_experience, job_experience):
    """
    Analyze the experience section of the resume against the job requirements.
    """
    # Implement logic to compare experience details
    return {"match_score": 80, "details": "Experience matches well with job requirements"}

def analyze_skills(resume_skills, job_skills):
    """
    Analyze the skills section of the resume against the job requirements.
    """
    # Implement logic to compare skills
    return {"match_score": 70, "details": "Some key skills are missing"}

def analyze_education(resume_education, job_education):
    """
    Analyze the education section of the resume against the job requirements.
    """
    # Implement logic to compare education details
    return {"match_score": 90, "details": "Education meets or exceeds requirements"}

def analyze_achievements(resume_achievements, job_achievements):
    """
    Analyze the achievements section of the resume against the job requirements.
    """
    # Implement logic to compare achievements
    return {"match_score": 60, "details": "Achievements are partially aligned"}

def calculate_overall_score(analysis):
    """
    Calculate an overall match score based on the analysis of different sections.
    """
    # Example: Weighted average of section scores
    weights = {"experience_match": 0.4, "skills_match": 0.3, "education_match": 0.2, "achievements_match": 0.1}
    overall_score = sum(analysis[section]["match_score"] * weight for section, weight in weights.items())
    return int(overall_score)

def generate_strengths(analysis):
    """
    Generate strengths based on the analysis.
    """
    return [f"{section}: {details['details']}" for section, details in analysis.items() if details["match_score"] > 75]

def generate_weaknesses(analysis):
    """
    Generate weaknesses based on the analysis.
    """
    return [f"{section}: {details['details']}" for section, details in analysis.items() if details["match_score"] < 50]

def generate_suggestions(analysis, job_requirements):
    """
    Generate suggestions for improvement based on the analysis and job requirements.
    """
    # Example: Suggest improving weak areas
    suggestions = []
    for section, details in analysis.items():
        if details["match_score"] < 75:
            suggestions.append(f"Improve {section} to better align with job requirements.")
    return suggestions

def fallback_match_resume_with_job(resume_text, job_description):
    """
    Fallback method to match resume with job description using TF-IDF and cosine similarity
    Used when the API call to Google's Gemini model fails
    """
    # Preprocess texts
    preprocessed_resume = preprocess_text(resume_text)
    preprocessed_job = preprocess_text(job_description)
    
    # Get skills from resume
    skills = extract_skills(resume_text)
    
    # Extract keywords from job description
    job_keywords = extract_keywords(job_description, top_n=15)
    
    # Calculate TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([preprocessed_resume, preprocessed_job])
    
    # Calculate cosine similarity
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    
    # Convert similarity to score (0-100)
    match_score = int(cosine_sim * 100)
    
    # Determine strengths based on skills that match job keywords
    strengths = [skill for skill in skills if any(keyword in skill.lower() for keyword in job_keywords)]
    
    # Determine weaknesses based on job keywords not found in resume
    resume_keywords = extract_keywords(resume_text, top_n=20)
    missing_keywords = [keyword for keyword in job_keywords 
                    if not any(keyword in resume_kw for resume_kw in resume_keywords)]
    
    # Generate suggestions
    suggestions = [
        f"Add or highlight experience with {keyword}" for keyword in missing_keywords[:3]
    ]
    suggestions.append("Use more specific examples of achievements related to the job requirements")
    
    return {
        "score": match_score,
        "strengths": strengths if strengths else ["No clear strengths identified"],
        "weaknesses": [f"Missing keyword: {keyword}" for keyword in missing_keywords[:5]] if missing_keywords else ["No specific weaknesses identified"],
        "suggestions": suggestions
    }

def suggest_jobs(resume_text, jobs_df):
    """
    Suggest jobs based on resume content
    
    Args:
        resume_text (str): Extracted text from the resume
        jobs_df (DataFrame): DataFrame containing job listings
        
    Returns:
        list: List of job suggestions with match scores
    """
    # Preprocess resume text
    preprocessed_resume = preprocess_text(resume_text)
    
    # Extract skills from resume
    skills = extract_skills(resume_text)
    skills_text = ' '.join(skills)
    
    # Create a combined text for matching
    combined_resume_text = preprocessed_resume + ' ' + skills_text
    
    # Create a list of texts to compare with resume
    job_texts = []
    for _, job in jobs_df.iterrows():
        job_text = f"{job['Job_Title']} {job['Company_Name']} {job.get('Description', '')}"
        job_texts.append(preprocess_text(job_text))
    
    # Calculate TF-IDF vectors
    vectorizer = TfidfVectorizer()
    all_texts = [combined_resume_text] + job_texts
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    
    # Calculate cosine similarity between resume and each job
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
    
    # Create a list of (index, similarity) tuples and sort by similarity
    job_similarities = [(i, cosine_similarities[0][i]) for i in range(len(job_texts))]
    job_similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Get top 5 matching jobs
    top_jobs = []
    for idx, similarity in job_similarities[:5]:
        job = jobs_df.iloc[idx].copy()
        job['Match_Score'] = int(similarity * 100)
        top_jobs.append(job.to_dict())
    
    return top_jobs