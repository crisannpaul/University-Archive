import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './DashboardUser.css';
import QRCodeList from '../QRCodeList/QRCodeList';
import {Store} from "react-notifications-component";

const UserDashboard = () => {
  const navigate = useNavigate();
  const [interactiveContent, setInteractiveContent] = useState([]);
  const [analysisResults, setAnalysisResults] = useState([]);
  const userID = sessionStorage.getItem('id');
  const [notifications, setNotifications] = useState([]);

  const data = {
    profile: {
      title: "Configure Profile",
      description: "Here you can configure your profile.",
      link: "/ConfigureUserProfile"
    },
    notifications: {
      title: "Password Reset",
      description: "Here you can reset your password.",
      link: "/PasswordReset"
    },
    donationCenters: {
      title: "Centers Map",
      description: "Here you will find the map for all donation centers.",
      link: "/DonationCenterMap"
    },
    requirements: {
      title: "Requirements",
      description: "See all possible people in need of donations.",
      link: "/donationRequests"
    },
    userProfile: {
      title: "User Profile",
      description: "Access your user profile.",
      link: "/userProfile"
    },
    recommendation: {
      title: "Get recommend",
      description: "Get your recommendation using AI.",
      link: "/RecommandUsingML"
    }
  };

  useEffect(() => {
    fetchInteractiveContent();
    fetchAnalysisResults();
    fetchNotifications();
  }, []);

  const fetchInteractiveContent = async () => {
    try {
      const response = await fetch('http://localhost:8080/api/v1/infoContent/all', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setInteractiveContent(data);
      } else {
        console.error('Failed to fetch content:', response.status);
      }
    } catch (error) {
      console.error('Error fetching content:', error);
    }
  };

  const fetchAnalysisResults = async () => {
    try {
      const response = await fetch(`http://localhost:8080/api/v1/analysisresult/user/${sessionStorage.getItem('id')}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setAnalysisResults(data);
      } else {
        console.error('Failed to fetch analysis results:', response.status);
      }
    } catch (error) {
      console.error('Error fetching analysis results:', error);
    }
  };

  const fetchNotifications = async () => {
    try {
      const response = await fetch(`http://localhost:8080/api/v1/dr/fetch-all/${sessionStorage.getItem('id')}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        console.log(data);
        setNotifications(data);
      } else {
        console.error('Failed to fetch notifications results:', response.status);
      }
    } catch (error) {
      console.error('Error fetching notifications results:', error);
    }
  };

  const handleClick = (link) => {
    navigate(link);
  };

  const handleNotification = async (notificationId) => {
    let lastAnalysis = null;
    try {
      const response = await fetch(`http://localhost:8080/api/v1/analysisresult/user/get_last/${sessionStorage.getItem('id')}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
      });
      if (response.ok) {
        lastAnalysis = await response.json();
        console.log(lastAnalysis);
      } else {
        console.error('Failed to fetch notifications2 results:', response.status);
      }
    } catch (error) {
      console.error('Error fetching notifications2 results:', error);
    }

    if (lastAnalysis == null || lastAnalysis.timestamp + 300 > (Math.round(new  Date().getTime() / 1000))){
      Store.addNotification({
        title: "INFO",
        message: "You can't donate right now",
        type: "danger",
        insert: "top",
        container: "top-right",
        dismiss: {
          duration: 1000,
          onScreen: true
        },
      })

      return;
    }

    try {
      const response = await fetch(`http://localhost:8080/api/v1/dr/${notificationId}/status/${sessionStorage.getItem("id")}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
      });
      if (response.ok) {
        const data = await response.json();
        console.log(data);
        if (data === false)
        {
          Store.addNotification({
            title: "INFO",
            message: "You can't donate right now",
            type: "danger",
            insert: "top",
            container: "top-right",
            dismiss: {
              duration: 1000,
              onScreen: true
            },
          })
        }
      } else {
        console.error('Failed to fetch notifications2 results:', response.status);
      }
    } catch (error) {
      console.error('Error fetching notifications2 results:', error);
    }
  }

  return (
    <>
      <div className="background-dash-user">
        <div className="analysis-results">
          <h2>Notifications</h2>
          <div className="results-list">
            {notifications.filter((not) => (not.status !== "COMPLETE"))
                .map((not) => (
                <div key={not.id} className="result-item">
                  <h4>Patient Name: {not.user.name}</h4>
                  <p>Donation Center: {not.donationCenter.name}</p>
                  <p>Status: {not.status}</p>
                  <button onClick={() => handleNotification(not.id)}>Confirm</button>
                </div>
            ))}
          </div>
        </div>
          <div className="dashboard">
            <div className="element profile" onClick={() => handleClick(data.profile.link)}>
              <h2>{data.profile.title}</h2>
              <p>{data.profile.description}</p>
            </div>
            <div className="element notifications" onClick={() => handleClick(data.notifications.link)}>
              <h2>{data.notifications.title}</h2>
              <p>{data.notifications.description}</p>
            </div>
            <div className="element donation-centers" onClick={() => handleClick(data.donationCenters.link)}>
              <h2>{data.donationCenters.title}</h2>
              <p>{data.donationCenters.description}</p>
            </div>
          
            <div className="element requirements" onClick={() => handleClick(data.requirements.link)}>
              <h2>{data.requirements.title}</h2>
              <p>{data.requirements.description}</p>
            </div>
            <div className="element user-profile" onClick={() => handleClick(data.userProfile.link)}>
              <h2>{data.userProfile.title}</h2>
              <p>{data.userProfile.description}</p>
            </div>
            <div className="element user-profile" onClick={() => handleClick(data.recommendation.link)}>
              <h2>{data.recommendation.title}</h2>
              <p>{data.recommendation.description}</p>
            </div>
          
            <div className="interactive-content">
              <h2>Informative Content</h2>
              <div className="content-list">
                {interactiveContent.map((content) => (
                  <div key={content.id} className="content-item">
                    <h4>{content.title}</h4>
                    <p>{content.description}</p>
                  </div>
                ))}
              </div>
            </div>

            <br></br>
            <br></br>
            <br></br>


            <div className="analysis-results">
            <h2>Analysis Results</h2>
            <div className="results-list">
              {analysisResults.map((result) => (
                <div key={result.id} className="result-item">
                  <h4>Results: {result.analysisDescription}</h4>
                </div>
              ))}
              <QRCodeList userID={userID} />
            </div>
            </div>
        </div>
      </div>
    </>
  );
};

export default UserDashboard;
