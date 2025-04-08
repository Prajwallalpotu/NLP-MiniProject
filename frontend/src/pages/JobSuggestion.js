import React, { useState } from 'react';
import { Container, Row, Col, Form, Button, Table, Spinner, Alert } from 'react-bootstrap';
import axios from 'axios';

const JobSuggestion = () => {
  const [resume, setResume] = useState(null);
  const [resumeName, setResumeName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [suggestions, setSuggestions] = useState(null);

  const handleResumeChange = (e) => {
    if (e.target.files[0]) {
      setResume(e.target.files[0]);
      setResumeName(e.target.files[0].name);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!resume) {
      setError('Please upload a resume file');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('resume', resume);
      
      const response = await axios.post('http://127.0.0.1:5000/api/job-suggestion', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setSuggestions(response.data.suggestions);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while processing your request');
    } finally {
      setLoading(false);
    }
  };

  const getMatchClass = (score) => {
    if (score >= 70) return 'table-success';
    if (score >= 40) return 'table-warning';
    return 'table-danger';
  };

  return (
    <Container>
      <h1 className="page-title">Job Suggestion</h1>
      
      <div className="form-container">
        <Form onSubmit={handleSubmit}>
          <Row>
            <Col>
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
          </Row>
          
          {error && <Alert variant="danger">{error}</Alert>}
          
          <div className="d-grid gap-2">
            <Button variant="primary" type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Spinner animation="border" size="sm" className="me-2" />
                  Finding Jobs...
                </>
              ) : (
                'Get Job Suggestions'
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
      
      {suggestions && !loading && (
        <div className="results-container">
          <h2 className="text-center mb-4">Recommended Jobs</h2>
          
          <div className="table-container">
            <Table striped hover responsive className="job-table">
              <thead>
                <tr>
                  <th>Job Title</th>
                  <th>Company</th>
                  <th>Location</th>
                  <th>Experience</th>
                  <th>CTC</th>
                  <th>Posted</th>
                  <th>Match Score</th>
                </tr>
              </thead>
              <tbody>
                {suggestions.length > 0 ? (
                  suggestions.map((job, index) => (
                    <tr key={index} className={getMatchClass(job.Match_Score)}>
                      <td>{job.Job_Title}</td>
                      <td>{job.Company_Name}</td>
                      <td>{job.Location}</td>
                      <td>{job.Experience}</td>
                      <td>{job.CTC}</td>
                      <td>{job.Posted}</td>
                      <td><strong>{job.Match_Score}%</strong></td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="7" className="text-center">No job suggestions found</td>
                  </tr>
                )}
              </tbody>
            </Table>
          </div>
        </div>
      )}
    </Container>
  );
};

export default JobSuggestion;