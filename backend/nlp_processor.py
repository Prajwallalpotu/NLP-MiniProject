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
    nltk.data.find('tokenizers/punkt_tab')  # Check for punkt_tab
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('punkt_tab')  # Download punkt_tab if missing

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