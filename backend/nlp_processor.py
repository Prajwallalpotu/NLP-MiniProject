import re
import nltk
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

def preprocess_text(text):
    """
    Preprocess text by removing special characters, lowercasing,
    removing stopwords, and lemmatizing
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and numbers
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    
    # Tokenize text
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    
    # Lemmatize tokens
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    
    # Join tokens back into text
    preprocessed_text = ' '.join(tokens)
    
    return preprocessed_text

def extract_features(texts, max_features=5000):
    """
    Extract TF-IDF features from texts
    
    Args:
        texts (list): List of text documents
        max_features (int): Maximum number of features to extract
        
    Returns:
        feature_matrix: TF-IDF feature matrix
        vectorizer: Fitted TF-IDF vectorizer
    """
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 2),  # Use unigrams and bigrams
        stop_words='english'
    )
    
    # Fit and transform texts
    feature_matrix = vectorizer.fit_transform(texts)
    
    return feature_matrix, vectorizer

def extract_keywords(text, top_n=10):
    """
    Extract the most important keywords from text using TF-IDF
    
    Args:
        text (str): Input text
        top_n (int): Number of top keywords to extract
        
    Returns:
        list: Top keywords
    """
    # Preprocess text
    preprocessed_text = preprocess_text(text)
    
    # Create document list with just the input text
    docs = [preprocessed_text]
    
    # Extract features
    vectorizer = TfidfVectorizer(
        max_features=1000,
        ngram_range=(1, 2),
        stop_words='english'
    )
    
    # Fit transform
    X = vectorizer.fit_transform(docs)
    
    # Get feature names
    feature_names = vectorizer.get_feature_names_out()
    
    # Get feature values
    feature_values = X.toarray()[0]
    
    # Sort features by importance
    sorted_idx = feature_values.argsort()[::-1]
    
    # Get top keywords
    top_keywords = [feature_names[i] for i in sorted_idx[:top_n]]
    
    return top_keywords

def extract_entities(text):
    """
    Extract named entities from text using spaCy
    
    Args:
        text (str): Input text
        
    Returns:
        dict: Dictionary with entity types and their values
    """
    import spacy
    
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        import subprocess
        import sys
        subprocess.call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        nlp = spacy.load("en_core_web_sm")
    
    doc = nlp(text)
    entities = {}
    
    for ent in doc.ents:
        if ent.label_ not in entities:
            entities[ent.label_] = []
        entities[ent.label_].append(ent.text)
    
    return entities

def extract_resume_sections(text):
    """
    Extract common resume sections based on headings
    
    Args:
        text (str): Resume text
        
    Returns:
        dict: Dictionary with section names and their content
    """
    # Common section headers in resumes
    section_headers = [
        'education', 'experience', 'work experience', 'employment', 'skills',
        'technical skills', 'professional skills', 'certifications', 'projects',
        'achievements', 'awards', 'publications', 'languages', 'interests',
        'summary', 'objective', 'profile', 'about me', 'personal information',
        'contact information', 'references', 'volunteer', 'activities'
    ]
    
    # Create pattern to match section headers
    header_pattern = '|'.join([fr'\b{re.escape(header)}\b' for header in section_headers])
    pattern = re.compile(fr'(?i)(^|\n)[\s\*]*({header_pattern})[\s\*]*(:|$|\n)', re.MULTILINE)
    
    # Find all section headers in the text
    matches = list(pattern.finditer(text))
    
    # Extract sections
    sections = {}
    for i, match in enumerate(matches):
        section_name = match.group(2).strip().lower()
        start_pos = match.end()
        
        # Determine end position (start of next section or end of text)
        if i < len(matches) - 1:
            end_pos = matches[i+1].start()
        else:
            end_pos = len(text)
        
        # Extract section content
        section_content = text[start_pos:end_pos].strip()
        sections[section_name] = section_content
    
    return sections