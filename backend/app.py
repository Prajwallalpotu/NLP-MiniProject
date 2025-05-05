from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
from werkzeug.utils import secure_filename
import pandas as pd
from resume_parser import extract_text_from_resume
from nlp_processor import preprocess_text, extract_features
from job_matcher import match_resume_with_job, suggest_jobs
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv("FRONTEND_URL", "http://localhost:3000")}}, 
     supports_credentials=True, allow_headers="*", methods=["GET", "POST", "OPTIONS"])

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    logger.warning("OPENAI_API_KEY is not set. Resume matching will use fallback method.")

# Load job dataset once
try:
    jobs_df = pd.read_csv(os.getenv("JOB_DATASET_PATH", './data/job.csv'))
    logger.info(f"Successfully loaded job dataset with {len(jobs_df)} entries")
except Exception as e:
    logger.error(f"Error loading job dataset: {e}")
    # Create an empty DataFrame with expected columns
    jobs_df = pd.DataFrame(columns=['Job_Title', 'Company_Name', 'Location', 'Experience', 'CTC', 'Posted'])

@app.route('/')
def index():
    return "Welcome to the Resume Matcher API!"

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Service is running"}), 200

@app.route('/api/resume-match', methods=['POST'])
def resume_match():
    logger.info("Request received at /api/resume-match")
    
    if 'resume' not in request.files or 'jobDescription' not in request.form:
        logger.warning("Missing resume or job description in request")
        return jsonify({"error": "Missing resume file or job description"}), 400
    
    resume_file = request.files['resume']
    job_description = request.form['jobDescription']
    
    if resume_file.filename == '':
        logger.warning("No resume file selected")
        return jsonify({"error": "No resume file selected"}), 400
    
    # Save the uploaded file temporarily
    temp_dir = tempfile.gettempdir()
    filename = secure_filename(resume_file.filename)
    file_path = os.path.join(temp_dir, filename)
    resume_file.save(file_path)
    
    try:
        # Process the resume
        logger.info(f"Extracting text from resume: {filename}")
        resume_text = extract_text_from_resume(file_path)
        
        if not resume_text or len(resume_text.strip()) < 10:
            logger.warning(f"Failed to extract meaningful text from resume: {filename}")
            return jsonify({"error": "Could not extract text from the resume. Please check the file format."}), 400
        
        # Match resume with job description
        logger.info("Matching resume with job description")
        match_results = match_resume_with_job(resume_text, job_description)
        
        # Clean up the temporary file
        os.remove(file_path)
        logger.info("Resume analysis completed successfully")
        
        return jsonify(match_results), 200
    
    except Exception as e:
        logger.error(f"Error processing resume: {e}")
        # Clean up in case of error
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({"error": str(e)}), 500

@app.route('/api/job-suggestion', methods=['POST','OPTIONS'])
def job_suggestion():
    if request.method == 'OPTIONS':
        return jsonify({'message': 'CORS preflight passed'}), 200
    if 'resume' not in request.files:
        return jsonify({"error": "Missing resume file"}), 400
    
    resume_file = request.files['resume']
    
    if resume_file.filename == '':
        return jsonify({"error": "No resume file selected"}), 400
    
    # Save the uploaded file temporarily
    temp_dir = tempfile.gettempdir()
    filename = secure_filename(resume_file.filename)
    file_path = os.path.join(temp_dir, filename)
    resume_file.save(file_path)
    
    try:
        # Process the resume
        resume_text = extract_text_from_resume(file_path)
        
        # Get job suggestions
        # Update column names to match your CSV file
        jobs_df.columns = jobs_df.columns.str.strip()  # Strip any extra whitespace
        jobs_df.rename(columns={
            'job_title': 'Job_Title',
            'company_name': 'Company_Name',
            'location': 'Location',
            'start_date': 'Start_Date',
            'ctc': 'CTC',
            'experience': 'Experience',
            'posted': 'Posted'
        }, inplace=True)
        
        suggestions = suggest_jobs(resume_text, jobs_df)
        
        # Clean up the temporary file
        os.remove(file_path)
        
        return jsonify({"suggestions": suggestions}), 200
    
    except Exception as e:
        # Clean up in case of error
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs(os.getenv("DATA_DIR", 'data'), exist_ok=True)
    
    # Check if jobs.csv exists, if not create a sample one
    if not os.path.exists(os.path.join(os.getenv("DATA_DIR", 'data'), 'jobs.csv')):
        sample_data = {
            'Job_Title': ['Software Engineer', 'Data Scientist', 'Product Manager'],
            'Company_Name': ['Tech Corp', 'Data Analytics Inc', 'Product Solutions'],
            'Location': ['San Francisco, CA', 'New York, NY', 'Seattle, WA'],
            'Start_Date': ['Immediate', 'May 2025', 'June 2025'],
            'CTC': ['$120,000', '$130,000', '$140,000'],
            'Experience': ['3-5 years', '2-4 years', '4-6 years'],
            'Posted': ['3 days ago', '1 week ago', '2 days ago']
        }
        pd.DataFrame(sample_data).to_csv(os.path.join(os.getenv("DATA_DIR", 'data'), 'jobs.csv'), index=False)
        print("Created sample jobs.csv")
    
    app.run(debug=True, port=5000)