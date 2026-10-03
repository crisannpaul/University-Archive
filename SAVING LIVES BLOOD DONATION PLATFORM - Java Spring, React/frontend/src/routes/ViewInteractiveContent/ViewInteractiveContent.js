import React, {useEffect, useState} from 'react';
import './ViewInteractiveContent.css';

const ViewInteractiveContent = () => {
  const [postedContent, setPostedContent] = useState([]);

  useEffect(() => {
    // Fetch existing content when the component mounts
    fetchPostedContent();
  }, []);

  const fetchPostedContent = async () => {
    try {
      const response = await fetch('http://localhost:8080/api/v1/interactive-content');
      if (response.ok) {
        const data = await response.json();
        setPostedContent(data);
      } else {
        console.error('Failed to fetch content:', response.status);
      }
    } catch (error) {
      console.error('Error fetching content:', error);
    }
  };

  return (
    <>

      <div className="background-dash-user"></div>
      <div className="view-content-container">
        <h2>Interactive Content</h2>
        <div className="posted-content-list">
          {postedContent.map((content) => (
            <div key={content.id} className="posted-content-item">
              <h4>{content.title}</h4>
              <p>{content.description}</p>
            </div>
          ))}
        </div>
      </div>
    </>
  );
};

export default ViewInteractiveContent;
