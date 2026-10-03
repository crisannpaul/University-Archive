 import React, {useEffect, useState} from 'react';
import './AnalysisResults.css';

const AnalysisForm = ({ onSubmit }) => {
  const [selectedPatient, setSelectedPatient] = useState('');
  const [analysisResults, setAnalysisResults] = useState('');
  const [eligibilityResult, setEligibilityResult] = useState(false);
  const [patients, setPatients] = useState([]);

  useEffect(() => {
    fetchPatients()
  }, [])

  const fetchPatients = async () => {
    try {
      const response = await fetch(`http://localhost:8080/api/v1/user/all`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setPatients(data);
      } else {
        console.error('Failed to fetch Patients:', response.status);
      }
    } catch (error) {
      console.error('Error fetching Patients:', error);
    }
  };

  const handleConfirmationChange = (e) => {
    setEligibilityResult(e.target.checked);
  };

  const handlePatientChange = (e) => {
    setSelectedPatient(e.target.value);
  };

  const handleAnalysisChange = (e) => {
    setAnalysisResults(e.target.value);
  };

  const handleSubmit = async () => {
    if (!selectedPatient || !analysisResults) {
      alert('Please select a patient and enter analysis results.');
      return;
    }

    const analysisData = {
      userId: selectedPatient,
      analysisDescription: analysisResults,
      eligibility: eligibilityResult
    };

    try {
      console.log(analysisData)
      const response = await fetch('http://localhost:8080/api/v1/analysisresult/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
        body: JSON.stringify(analysisData)
      });
  
      if (response.ok) {
        alert('Analysis results submitted successfully.');
        setSelectedPatient('');
        setAnalysisResults('');
        setEligibilityResult(false);
      } else {
        console.error('Failed to submit analysis results:', response.status);
        alert('Failed to submit analysis results. Please try again later.');
      }
    } catch (error) {
      console.error('Error submitting analysis results:', error);
      alert('An error occurred while submitting analysis results. Please try again later.');
    }
  };

  return (
    <>

      <div className="background-image-analysis">
        <div className="analysis-form">
          <h2>Submit Analysis</h2>
          <div className="form-group">
            <label htmlFor="patient">Patient:</label>
            <select id="patient" value={selectedPatient} onChange={handlePatientChange}>
              <option value="">Select a patient</option>
              {patients.map((patient) => (
                <option key={patient.id} value={patient.id}>
                  {patient.name}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="analysis">Analysis Results:</label>
            <textarea id="analysis" value={analysisResults} onChange={handleAnalysisChange} />
          </div>
          <div className="checkbox-group">
            <label>
              <input type="checkbox" checked={eligibilityResult} onChange={handleConfirmationChange} />
             Eligible?
            </label>
          </div>
          <button className="button-analysis" onClick={handleSubmit}>Submit</button>
        </div>
      </div>
    </>
  );
  
}
export default AnalysisForm;
