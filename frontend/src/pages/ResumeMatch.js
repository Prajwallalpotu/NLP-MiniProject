import React, { useState } from 'react';
import { Container, Row, Col, Form, Button, Card, ListGroup, Spinner, Alert } from 'react-bootstrap';
import axios from 'axios';

const ResumeMatch = () => {
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [resumeName, setResumeName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);

  const handleResumeChange = (e) => {
    if (e.target.files[0]) {
      setResume(e.target.files[0]);
      setResumeName(e.target.files[0].name);
    }
  };

  const handleJobDescriptionChange = (e) => {
    setJobDescription(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!resume) {
      setError('Please upload a resume file');
      return;
    }
    
    if (!jobDescription.trim()) {
      setError('Please enter a job description');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('resume', resume);
      formData.append('jobDescription', jobDescription);
      
      const response = await axios.post('http://127.0.0.1:5000//api/resume-match', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Access-Control-Allow-Origin': '*', // Add this header for debugging
        }
      });
      
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while processing your request');
    } finally {
      setLoading(false);
    }
  };

  const getScoreClass = (score) => {
    if (score >= 70) return 'score-high';
    if (score >= 40) return 'score-medium';
    return 'score-low';
  };

  return (
    <Container>
      <h1 className="page-title">Resume Match</h1>
      
      <div className="form-container">
        <Form onSubmit={handleSubmit}>
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Upload Resume</Form.Label>
                <div className="upload-box" onClick={() => document.getElementById('resumeUpload').click()}>
                  <input
                    id="resumeUpload"
                    type="file"
                    accept=".pdf,.doc,.docx,.txt"
                    onChange={handleResumeChange}
                    style={{ display: 'none' }}
                  />
                  {resumeName ? (
                    <p className="mb-0">Selected file: {resumeName}</p>
                  ) : (
                    <p className="mb-0">Click to upload resume (PDF, DOC, DOCX, TXT)</p>
                  )}
                </div>
              </Form.Group>
            </Col>
            
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Job Description</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={6}
                  placeholder="Paste the job description here..."
                  value={jobDescription}
                  onChange={handleJobDescriptionChange}
                />
              </Form.Group>
            </Col>
          </Row>
          
          {error && <Alert variant="danger">{error}</Alert>}
          
          <div className="d-grid gap-2">
            <Button variant="primary" type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Spinner animation="border" size="sm" className="me-2" />
                  Analyzing...
                </>
              ) : (
                'Match Resume'
              )}
            </Button>
          </div>
        </Form>
      </div>
      
      {loading && (
        <div className="loading-spinner">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </div>
      )}
      
      {results && !loading && (
        <div className="results-container">
          <h2 className="text-center mb-4">Match Results</h2>
          
          <Row className="mb-4">
            <Col className="text-center">
              <div className={`score-circle ${getScoreClass(results.score)}`}>
                {results.score}%
              </div>
              <p className="lead">Match Score</p>
            </Col>
          </Row>
          
          <Row>
            <Col md={6} className="mb-4">
              <div className="section-title">Strengths</div>
              <ListGroup>
                {results.strengths && results.strengths.length > 0 ? (
                  results.strengths.map((strength, index) => (
                    <ListGroup.Item key={index}>✅ {strength}</ListGroup.Item>
                  ))
                ) : (
                  <ListGroup.Item>No specific strengths identified</ListGroup.Item>
                )}
              </ListGroup>
            </Col>
            
            <Col md={6} className="mb-4">
              <div className="section-title">Areas for Improvement</div>
              <ListGroup>
                {results.weaknesses && results.weaknesses.length > 0 ? (
                  results.weaknesses.map((weakness, index) => (
                    <ListGroup.Item key={index}>⚠️ {weakness}</ListGroup.Item>
                  ))
                ) : (
                  <ListGroup.Item>No specific weaknesses identified</ListGroup.Item>
                )}
              </ListGroup>
            </Col>
          </Row>
          
          <Row>
            <Col>
              <div className="section-title">Suggestions</div>
              <ListGroup>
                {results.suggestions && results.suggestions.length > 0 ? (
                  results.suggestions.map((suggestion, index) => (
                    <ListGroup.Item key={index}>💡 {suggestion}</ListGroup.Item>
                  ))
                ) : (
                  <ListGroup.Item>No specific suggestions available</ListGroup.Item>
                )}
              </ListGroup>
            </Col>
          </Row>
        </div>
      )}
    </Container>
  );
};

export default ResumeMatch;