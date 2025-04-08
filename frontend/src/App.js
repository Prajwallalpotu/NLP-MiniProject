import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import NavigationBar from './components/NavigationBar';
import Home from './pages/Home';
import ResumeMatch from './pages/ResumeMatch';
import JobSuggestion from './pages/JobSuggestion';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  return (
    <Router>
      <NavigationBar />
      <Container className="mt-4">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/resume-match" element={<ResumeMatch />} />
          <Route path="/job-suggestion" element={<JobSuggestion />} />
        </Routes>
      </Container>
    </Router>
  );
}

export default App;