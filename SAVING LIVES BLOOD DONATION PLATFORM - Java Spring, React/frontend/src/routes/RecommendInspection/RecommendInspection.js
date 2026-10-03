import React, { useEffect, useState } from 'react';
import './RecommendInspection.css';

const RecommendInspection = () => {
  const [symptomes, setSymptomes] = useState('');
  const [recommend, setRecommand] = useState('');
  const [displayed, setDisplayed] = useState(false);

  useEffect(() => {
    setDisplayed(true);
  }, [recommend])

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch('http://localhost:8080/api/diagnosis/get', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
        body: JSON.stringify(symptomes)
      });
      if (response.ok) {
        alert('Recommendation submitted successfully! :)');
        setSymptomes('');
        const data = await response.json();
        setRecommand(data.diagnosis);
      } else {
        console.error('Failed to submit recommendation: :(', response.status);
        alert('Failed to submit recommendation. Please try again.');
      }
    } catch (error) {
      console.error('Error submitting recommendation: :/', error);
      alert('An error occurred. Please try again later.');
    }
  };

  return (
    <div className="recommend-inspection-container">
      <h2>Get recommendation using AI</h2>
      <form onSubmit={handleSubmit} className="recommend-form">
        <label>
          Symptomes:
          <textarea
            value={symptomes}
            onChange={(e) => setSymptomes(e.target.value)}
            required
            className="input"
          />
        </label>
        <button type="submit" className="submit-button">Submit Recommendation</button>
      </form>
      { displayed &&
          <textarea
              value={recommend}
              className="input"
              disabled={true}
          />}
    </div>
  );
};

export default RecommendInspection;
