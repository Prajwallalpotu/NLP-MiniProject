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
    Match a resume with a job description using Google's Gemini model
    
    Args:
        resume_text (str): Extracted text from the resume
        job_description (str): Job description text
        
    Returns:
        dict: Match results including score, strengths, weaknesses, and suggestions
    """
    # Use Google's Gemini model to analyze the match
    prompt = f"""
    I have a resume and a job description. I need you to analyze how well the resume matches the job description.
    
    RESUME:
    {resume_text}
    
    JOB DESCRIPTION:
    {job_description}
    
    Based on the job description, provide:
    1. A score (0 to 100) based on the match.
    2. Strengths of the resume.
    3. Weaknesses or missing areas.
    4. Suggestions to improve for this specific job.
    
    Format your response as JSON with these keys: score, strengths, weaknesses, suggestions
    """

    try:
        # Get API key from environment variables
        api_key = os.getenv("GENAI_API_KEY")
        if not api_key:
            raise ValueError("GenAI API key not found in environment variables.")
        
        # Create a client with the API key
        client = genai.Client(api_key=api_key)
        
        # Generate content
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        
        # Extract the response text
        response_text = response.text
        
        # Try to parse JSON from the response
        try:
            import json
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # If JSON parsing fails, extract the information manually
            lines = response_text.split('\n')
            result = {}
            
            # Initialize sections
            current_section = None
            sections = {
                'score': '',
                'strengths': [],
                'weaknesses': [],
                'suggestions': []
            }
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for section headers
                if 'score' in line.lower() and ':' in line:
                    current_section = 'score'
                    score_text = line.split(':', 1)[1].strip()
                    # Extract numeric value
                    import re
                    score_match = re.search(r'\d+', score_text)
                    if score_match:
                        sections['score'] = int(score_match.group())
                    else:
                        sections['score'] = 0  # Default if no number found
                
                elif 'strength' in line.lower() and ':' in line:
                    current_section = 'strengths'
                    continue
                
                elif 'weakness' in line.lower() and ':' in line:
                    current_section = 'weaknesses'
                    continue
                
                elif 'suggestion' in line.lower() and ':' in line:
                    current_section = 'suggestions'
                    continue
                
                # Add content to current section
                if current_section == 'score':
                    continue  # Already handled above
                elif current_section in ['strengths', 'weaknesses', 'suggestions']:
                    # If line starts with a number or bullet, clean it
                    cleaned_line = re.sub(r'^\d+\.\s*|\*\s*|-\s*', '', line).strip()
                    if cleaned_line:
                        sections[current_section].append(cleaned_line)
            
            result = sections
            
        # Ensure we have all required keys
        required_keys = ['score', 'strengths', 'weaknesses', 'suggestions']
        for key in required_keys:
            if key not in result:
                if key == 'score':
                    result[key] = 0
                else:
                    result[key] = []
                    
        # Convert score to integer if it's not already
        if isinstance(result['score'], str):
            try:
                result['score'] = int(result['score'])
            except ValueError:
                result['score'] = 0
        
        return result
    
    except Exception as e:
        # Fallback to TF-IDF based matching if API call fails
        return fallback_match_resume_with_job(resume_text, job_description)

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