import React from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <Container>
      <Row className="text-center mb-5">
        <Col>
          <h1 className="display-4">Resume Analysis & Job Matching</h1>
          <p className="lead">Enhance your job search with our NLP-powered resume analysis tools</p>
        </Col>
      </Row>

      <Row>
        <Col md={6} className="mb-4">
          <Card className="h-100">
            <Card.Body className="d-flex flex-column">
              <Card.Title>Resume Match</Card.Title>
              <Card.Text>
                Upload your resume and a job description to see how well you match the position.
                Get detailed feedback on your strengths, weaknesses, and suggestions for improvement.
              </Card.Text>
              <div className="mt-auto">
                <Button as={Link} to="/resume-match" variant="primary">Try Resume Match</Button>
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6} className="mb-4">
          <Card className="h-100">
            <Card.Body className="d-flex flex-column">
              <Card.Title>Job Suggestion</Card.Title>
              <Card.Text>
                Upload your resume and get personalized job recommendations based on your skills, 
                experience, and qualifications. Find the perfect job match for your profile.
              </Card.Text>
              <div className="mt-auto">
                <Button as={Link} to="/job-suggestion" variant="primary">Try Job Suggestion</Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="mt-5">
        <Col>
          <Card>
            <Card.Body>
              <Card.Title>How It Works</Card.Title>
              <Card.Text>
                Our system uses advanced Natural Language Processing techniques including:
              </Card.Text>
              <ul>
                <li>Text extraction from various document formats (PDF, DOCX)</li>
                <li>Tokenization and feature extraction</li>
                <li>TF-IDF vectorization for content matching</li>
                <li>Semantic analysis using Google's Gemini AI model</li>
                <li>Skill extraction and keyword matching</li>
                <li>Cosine similarity for job recommendations</li>
              </ul>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Home;
