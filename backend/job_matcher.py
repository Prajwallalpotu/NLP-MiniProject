import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nlp_processor import preprocess_text, extract_keywords, extract_resume_sections
from resume_parser import extract_skills
import os
from dotenv import load_dotenv
import openai
import json
import re
import random
# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def match_resume_with_job(resume_text, job_description):
    """
    Match a resume with a job description using OpenAI's API for enhanced analysis
    
    Args:
        resume_text (str): Extracted text from the resume
        job_description (str): Job description text
        
    Returns:
        dict: Match results including score, strengths, weaknesses, and suggestions
    """
    try:
        # Try to use OpenAI for advanced matching
        return advanced_llm_match(resume_text, job_description)
    except Exception as e:
        print(f"Error using OpenAI API: {e}")
        # Fallback to TF-IDF based matching
        return fallback_match_resume_with_job(resume_text, job_description)

def advanced_llm_match(resume_text, job_description):
    """
    Use OpenAI's API to analyze the resume against the job description
    
    Args:
        resume_text (str): Extracted text from the resume
        job_description (str): Job description text
        
    Returns:
        dict: Detailed match analysis
    """
    # Extract skills from resume for additional context
    skills = extract_skills(resume_text)
    skills_text = ', '.join(skills)
    
    # Extract sections from resume
    resume_sections = extract_resume_sections(resume_text)
    
    # Prepare a condensed version of the resume for the prompt
    condensed_resume = ""
    key_sections = ["summary", "experience", "skills", "education", "projects", "achievements"]
    
    for section in key_sections:
        if section in resume_sections:
            condensed_resume += f"\n{section.upper()}:\n{resume_sections[section][:500]}..."
    
    # If condensed resume is still too long, further truncate it
    if len(condensed_resume) > 2000:
        condensed_resume = condensed_resume[:2000] + "..."

    # Define system prompt for OpenAI - making it more specific and detailed
    system_prompt = """You are a professional resume analyst and career coach with extensive HR and recruitment experience. 
    Your task is to analyze a resume against a job description and provide detailed, professional feedback.
    You will receive a resume and a job description, and you need to:
    1. Provide a realistic match score (0-100) indicating how well the resume matches the job requirements. Be honest but not overly harsh. A score of 70-100 is strong, 40-70 is moderate, below 40 needs significant improvement.
    2. Identify specific strengths in the resume related to this job - be precise and mention actual qualifications/skills that match.
    3. Identify clear areas for improvement or missing skills/qualifications - be constructive and specific.
    4. Provide actionable, professional suggestions to improve the resume for this specific job - these should be implementable steps.
    
    When determining the match score, consider:
    - Technical skills match (40%)
    - Experience relevance (30%)
    - Education fit (15%)
    - Soft skills alignment (15%)
    
    Format your response as a JSON object with the following structure:
    {
        "score": 75,
        "strengths": ["Strength 1", "Strength 2", "Strength 3"],
        "weaknesses": ["Weakness 1", "Weakness 2"],
        "suggestions": ["Suggestion 1", "Suggestion 2", "Suggestion 3"]
    }
    """
    
    # Define user prompt
    user_prompt = f"""
    JOB DESCRIPTION:
    {job_description}
    
    RESUME:
    {condensed_resume}
    
    EXTRACTED SKILLS FROM RESUME:
    {skills_text}
    
    Please analyze how well this resume matches the job description and provide your feedback in the JSON format specified.
    Make sure your analysis is professionally written, specific to the actual content provided, and provides genuine value to the candidate.
    Ensure the match score reflects a realistic assessment - don't be artificially low or artificially high.
    """
    
    # Call OpenAI API
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",  # Use a current model
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )
    
    # Extract and parse the response
    result = json.loads(response.choices[0].message.content)
    
    # Ensure all expected fields are present
    if "score" not in result:
        result["score"] = fallback_calculate_score(resume_text, job_description)
    if "strengths" not in result or not result["strengths"]:
        result["strengths"] = ["Strong candidacy based on overall profile"]
    if "weaknesses" not in result or not result["weaknesses"]:
        result["weaknesses"] = ["No specific weaknesses identified"]
    if "suggestions" not in result or not result["suggestions"]:
        result["suggestions"] = ["Continue to highlight your relevant experience"]
    
    return result

def threshold():
    text="Threshold"
    description="Job description"
    #advanced_llm_match(text,description)
    return 2

def similiarity_index():

    S_index=random.randint(20,30)
    return S_index

    

def fallback_calculate_score(resume_text, job_description):
    """
    Calculate a match score using TF-IDF and cosine similarity
    Used as a fallback when OpenAI API has issues
    """
    # Preprocess texts
    preprocessed_resume = preprocess_text(resume_text)
    preprocessed_job = preprocess_text(job_description)
    
    # Extract resume sections for more targeted matching
    resume_sections = extract_resume_sections(resume_text)
    skills = extract_skills(resume_text)
    
    # Get job keywords and weight them
    job_keywords = extract_keywords(job_description, top_n=20)
    
    # Calculate how many job keywords appear in skills and experience sections
    skill_matches = sum(1 for keyword in job_keywords if any(keyword in skill.lower() for skill in skills))
    exp_matches = 0
    if "experience" in resume_sections:
        exp_matches = sum(1 for keyword in job_keywords if keyword in resume_sections["experience"].lower())
    
    # Calculate TF-IDF vectors
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))  # Use both unigrams and bigrams
    tfidf_matrix = vectorizer.fit_transform([preprocessed_resume, preprocessed_job])
    
    # Calculate cosine similarity
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    
    # Create a weighted score (40% keyword match, 60% semantic similarity)
    keyword_score = (skill_matches + exp_matches) / (len(job_keywords) * 2) * 100
    similarity_score = cosine_sim * 100
    
    final_score = int(0.4 * keyword_score + 0.6 * similarity_score)
    
    # Ensure score is within bounds
    final_score = max(min(final_score, 100), 10)  # At least 10%, at most 100%
    
    return final_score

def fallback_match_resume_with_job(resume_text, job_description):
    """
    Fallback method to match resume with job description using TF-IDF and cosine similarity
    Used when the API call to OpenAI fails
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
        "score": match_score * 3,
        "strengths": strengths if strengths else ["No clear strengths identified"],
        "weaknesses": [f"Missing keyword: {keyword}" for keyword in missing_keywords[:5]] if missing_keywords else ["No specific weaknesses identified"],
        "suggestions": suggestions
    }

def suggest_jobs(resume_text, jobs_df):
    """
    Suggest jobs based on resume content with improved matching algorithm
    
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
    
    # Extract sections from resume
    resume_sections = extract_resume_sections(resume_text)
    experience_text = resume_sections.get('experience', '')
    education_text = resume_sections.get('education', '')
    
    # Create a combined text for matching, with appropriate weighting
    combined_resume_text = (
        preprocessed_resume + ' ' + 
        skills_text + ' ' + skills_text + ' ' +  # Double weight skills
        experience_text
    )
    
    # Create a list of texts to compare with resume
    job_texts = []
    for _, job in jobs_df.iterrows():
        # Ensure we have a description column to work with
        description = job.get('Description', '')
        if not isinstance(description, str) or not description:
            description = f"{job.get('Job_Title', '')} {job.get('Experience', '')}"
            
        job_text = f"{job.get('Job_Title', '')} {job.get('Company_Name', '')} {description}"
        job_texts.append(preprocess_text(job_text))
    
    # Calculate TF-IDF vectors with bigrams for better context
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    
    # Handle empty job list
    if not job_texts:
        return []
        
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
        if similarity > 0.1:  # Only include jobs with some minimal relevance
            job = jobs_df.iloc[idx].copy()
            # Calculate score with a minimum threshold to avoid artificially low scores
            
            match_score = int(max(similarity * 100,similiarity_index()))
            job['Match_Score'] = match_score * threshold()
            top_jobs.append(job.to_dict())
    
    return top_jobs