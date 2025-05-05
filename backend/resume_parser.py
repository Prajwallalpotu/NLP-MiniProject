import PyPDF2
import docx
import re
import spacy
from spacy.matcher import Matcher
import os

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess
    subprocess.call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

def extract_text_from_resume(file_path):
    """
    Extract text from resume file (supports PDF, DOCX, and TXT)
    
    Args:
        file_path (str): Path to the resume file
        
    Returns:
        str: Extracted text from the resume
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension == '.docx':
        return extract_text_from_docx(file_path)
    elif file_extension == '.doc':
        return extract_text_from_doc(file_path)
    elif file_extension == '.txt':
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return ""

def extract_text_from_doc(file_path):
    """
    For DOC files, we'll use a simple placeholder.
    In a production environment, you would use a library like antiword,
    textract, or a conversion service.
    """
    # This is a placeholder and should be replaced with actual DOC extraction
    return "DOC file format detected. Please convert to DOCX or PDF for better results."

def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error extracting text from TXT: {e}")
        return ""

def extract_skills(text):
    """
    Extract skills from resume text using spaCy NER and pattern matching
    
    Args:
        text (str): Resume text
        
    Returns:
        list: List of skills found in the text
    """
    # Common tech skills
    skills_db = [
        'machine learning', 'deep learning', 'neural networks', 'artificial intelligence',
        'python', 'r', 'java', 'c++', 'c#', 'javascript', 'typescript', 'ruby', 'perl',
        'php', 'html', 'css', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'oracle',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'ci/cd',
        'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'agile', 'scrum',
        'kanban', 'waterfall', 'devops', 'sre', 'data science', 'data analysis',
        'data engineering', 'data visualization', 'tableau', 'power bi', 'excel',
        'pandas', 'numpy', 'scipy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras',
        'nlp', 'computer vision', 'opencv', 'reinforcement learning', 'a/b testing',
        'etl', 'spark', 'hadoop', 'hive', 'pig', 'kafka', 'airflow', 'luigi',
        'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring',
        'hibernate', 'asp.net', 'rest', 'graphql', 'soap', 'microservices', 'serverless',
        'blockchain', 'solidity', 'smart contracts', 'web3', 'ethereum', 'golang', 'rust',
        'swift', 'objective-c', 'kotlin', 'android', 'ios', 'react native', 'flutter',
        'linux', 'unix', 'windows', 'macos', 'bash', 'powershell', 'shell scripting',
        'networking', 'tcp/ip', 'http', 'https', 'dns', 'load balancing', 'nginx', 'apache',
        'security', 'encryption', 'authentication', 'authorization', 'oauth', 'jwt',
        'penetration testing', 'vulnerability assessment', 'firewall', 'vpn',
        'project management', 'product management', 'leadership', 'team management',
        'communication', 'presentation', 'negotiation', 'critical thinking',
        'problem solving', 'decision making', 'time management', 'budgeting',
        'forecasting', 'strategic planning', 'risk management', 'quality assurance',
        'testing', 'selenium', 'cypress', 'jest', 'mocha', 'pytest', 'junit',
        'continuous integration', 'continuous deployment', 'continuous delivery',
        'data warehousing', 'data modeling', 'data mining', 'business intelligence',
        'machine learning operations', 'mlops', 'aiops', 'devsecops', 'cloud computing',
        'saas', 'paas', 'iaas', 'faas', 'iot', 'embedded systems', 'fpga', 'vhdl',
        'verilog', 'pcb design', 'digital signal processing', 'control systems',
        'robotics', 'automation', 'plc', 'scada', 'hmi', 'crm', 'salesforce',
        'dynamics', 'erp', 'sap', 'oracle', 'peoplesoft', 'workday', 'service now',
        'itil', 'itsm', 'technical writing', 'user experience', 'user interface',
        'wireframing', 'prototyping', 'figma', 'sketch', 'adobe xd', 'photoshop',
        'illustrator', 'indesign', 'after effects', 'premiere pro', 'final cut',
        'avid', 'maya', 'blender', 'autocad', 'revit', 'solidworks', 'catia',
        'marketing', 'digital marketing', 'seo', 'sem', 'ppc', 'social media',
        'content creation', 'copywriting', 'email marketing', 'affiliate marketing',
        'analytics', 'google analytics', 'ab testing', 'conversion optimization',
        'customer experience', 'customer journey', 'user research', 'usability testing',
        'accessibility', 'wcag', 'section 508', 'ada compliance', 'localization',
        'internationalization', 'technical support', 'helpdesk', 'service desk',
        'incident management', 'problem management', 'change management',
        'release management', 'configuration management', 'asset management',
        'procurement', 'vendor management', 'contract negotiation', 'legal',
        'regulatory compliance', 'gdpr', 'ccpa', 'hipaa', 'sox', 'pci dss',
        'iso 27001', 'nist', 'cis', 'cybersecurity', 'intrusion detection',
        'intrusion prevention', 'siem', 'soar', 'dlp', 'endpoint protection',
        'mobile device management', 'identity management', 'privileged access',
        'active directory', 'ldap', 'kerberos', 'biometric authentication',
        'cryptography', 'pki', 'digital signatures', 'blockchain', 'distributed ledger',
        'smart contracts', 'defi', 'nft', 'web3', 'cryptocurrency', 'bitcoin',
        'ethereum', 'solana', 'cardano', 'polkadot', 'avalanche', 'consensys'
    ]
    
    # Initialize matcher with the spaCy vocab
    matcher = Matcher(nlp.vocab)
    
    # Add patterns for the skills matcher
    patterns = []
    for skill in skills_db:
        skill_tokens = skill.split()
        if len(skill_tokens) == 1:
            pattern = [{"LOWER": skill_tokens[0]}]
        else:
            pattern = [{"LOWER": token} for token in skill_tokens]
        matcher.add(skill, [pattern])
    
    # Process the text
    doc = nlp(text.lower())
    
    # Initialize a set to store unique skills
    skills_found = set()
    
    # Match skills in the text
    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        skill = span.text.lower()
        # Exclude common words that might be mistakenly identified as skills
        if len(skill) > 2 and skill not in ['the', 'and', 'for', 'with']:
            skills_found.add(skill)
    
    # Add any skills that were directly mentioned
    for skill in skills_db:
        if re.search(r'\b' + re.escape(skill) + r'\b', text.lower()):
            skills_found.add(skill)
    
    # Convert set to list and sort alphabetically
    return sorted(list(skills_found))