import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './DoctorDashboard.css';
import Navbar from '../Navbar/Navbar';


const DoctorDashboard = () => {
  const navigate = useNavigate(); // Initialize useNavigate

  const [interactiveContent, setInteractiveContent] = useState([]);

  useEffect(() => {
    fetchInteractiveContent();
  }, []);

  const fetchInteractiveContent = async () => {
    try {
      const response = await fetch('http://localhost:8080/api/v1/interactive-content');
      if (response.ok) {
        const data = await response.json();
        setInteractiveContent(data);
      } else {
        console.error('Failed to fetch interactive content:', response.status);
      }
    } catch (error) {
      console.error('Error fetching interactive content:', error);
    }
  };

  const data = {
    registerCalls: {
      title: "Donation Calls",
      description: "Register new donation calls.",
      link: "/CallRegistrationSystem"
    },
    interactiveContent: {
      title: "Interactive Content",
      description: "See the interactive content posted by admin.",
      link: "/viewIneractiveContent"
    },
    postAnalysis: {
      title: "Post Analysis Results",
      description: "Post analysis results for donors.",
      link: "/analysisResults"
    },
    donationRequests: {
      title: "Donation Requests",
      description: "See all possible donation requests.",
      link: "/donationRequests"
    },
    recommendInspection: {
      title: "Recommend Inspection",
      description: "Recommend a medical inspection to a donor.",
      link: "/RecommandUsingML"
    }
  };

  const handleClick = (link) => {
    navigate(link);
  };

  return (
    <>
      <div className="dashboard-doctor-1">
      <div className="dashboard">
        <div className="element register-calls" onClick={() => handleClick(data.registerCalls.link)}>
          <h2>{data.registerCalls.title}</h2>
          <p>{data.registerCalls.description}</p>
        </div>
        <div className="element interactive-content" onClick={() => handleClick(data.interactiveContent.link)}>
          <h2>{data.interactiveContent.title}</h2>
          <p>{data.interactiveContent.description}</p>
        </div>
        <div className="element post-analysis" onClick={() => handleClick(data.postAnalysis.link)}>
          <h2>{data.postAnalysis.title}</h2>
          <p>{data.postAnalysis.description}</p>
        </div>
        <div className="element donation-requests" onClick={() => handleClick(data.donationRequests.link)}>
          <h2>{data.donationRequests.title}</h2>
          <p>{data.donationRequests.description}</p>
        </div>
        <div className="element recommend-inspection" onClick={() => handleClick(data.recommendInspection.link)}>
          <h2>{data.recommendInspection.title}</h2>
          <p>{data.recommendInspection.description}</p>
        </div>
      </div>

      <div className="interactive-content-container">
        <h2>Interactive Content</h2>
        <ul>
          {interactiveContent.map(content => (
            <li key={content.id} className="interactive-content-item">
              <h3>{content.title}</h3>
              <p>{content.description}</p>
            </li>
          ))}
        </ul>
      </div>
      </div>
    </>
  );
};

export default DoctorDashboard;
