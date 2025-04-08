import os
import PyPDF2
import docx
import re
import nltk
from nltk.corpus import stopwords

# Download NLTK resources if not already present
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

def extract_text_from_pdf(pdf_path):
    """Extract text content from a PDF file."""
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text

def extract_text_from_docx(docx_path):
    """Extract text content from a DOCX file."""
    doc = docx.Document(docx_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_resume(file_path):
    """Extract text from resume based on file extension."""
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)
    elif file_extension in ['.txt']:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    else:
        raise ValueError(f"Unsupported file format: {file_extension}. Please upload PDF, DOCX, or TXT files.")

def extract_skills(text):
    """Extract potential skills from the resume text."""
    # Common technical skills that might appear in a resume
    common_skills = [
        'python', 'java', 'javascript', 'html', 'css', 'react', 'angular', 'vue', 
        'node', 'express', 'flask', 'django', 'spring', 'sql', 'nosql', 'mongodb',
        'mysql', 'postgresql', 'aws', 'azure', 'gcp', 'docker', 'kubernetes',
        'machine learning', 'deep learning', 'ai', 'nlp', 'data science',
        'data analysis', 'statistics', 'r', 'tableau', 'power bi', 'excel',
        'word', 'powerpoint', 'photoshop', 'illustrator', 'figma', 'sketch',
        'git', 'github', 'agile', 'scrum', 'jira', 'confluence'
    ]
    
    # Normalize text
    text_lower = text.lower()
    
    # Find skills
    found_skills = []
    for skill in common_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            found_skills.append(skill)
    
    return found_skills

def extract_education(text):
    """Extract education information from the resume text."""
    education_keywords = [
        'bachelor', 'master', 'phd', 'doctorate', 'degree', 'bs', 'ms', 'ba', 'ma',
        'b.tech', 'm.tech', 'b.e.', 'm.e.', 'b.sc', 'm.sc', 'university', 'college',
        'institute', 'school'
    ]
    
    text_lower = text.lower()
    education_info = []
    
    for keyword in education_keywords:
        pattern = r'(?i)([^.]*\b' + re.escape(keyword) + r'\b[^.]*\.)'
        matches = re.findall(pattern, text)
        education_info.extend(matches)
    
    # Remove duplicates and clean up
    education_info = list(set(education_info))
    education_info = [info.strip() for info in education_info if len(info.strip()) > 10]
    
    return education_info

def extract_experience(text):
    """Extract work experience information from the resume text."""
    experience_keywords = [
        'experience', 'work', 'employment', 'job', 'career', 'position',
        'role', 'worked at', 'employed at', 'internship'
    ]
    
    text_lower = text.lower()
    experience_info = []
    
    for keyword in education_keywords:
        pattern = r'(?i)([^.]*\b' + re.escape(keyword) + r'\b[^.]*\.)'
        matches = re.findall(pattern, text)
        experience_info.extend(matches)
    
    # Remove duplicates and clean up
    experience_info = list(set(experience_info))
    experience_info = [info.strip() for info in experience_info if len(info.strip()) > 10]
    
    return experience_info