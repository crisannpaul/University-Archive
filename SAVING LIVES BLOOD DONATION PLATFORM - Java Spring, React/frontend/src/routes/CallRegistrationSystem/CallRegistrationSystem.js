import React, {useEffect, useState} from 'react';
import './CallRegistrationSystem.css'

const CallRegistrationSystem = ({ onCallRegister }) => {
  const [donors, setDonors] = useState([]);
  const [donationCenters, setDonationCenters] = useState([]);
  const [formData, setFormData] = useState({
    donorId: '',
    donationCenterId: '',
  });

  const [callLogs, setCallLogs] = useState([]);

  const handleCallRegister = (callData) => {
    setCallLogs([...callLogs, callData]);
  };

  useEffect(() => {
    // Fetch donor names
    fetchDonors();
    // Fetch donation center locations
    fetchDonationCenters();
  }, []);

  const fetchDonors = async () => {
    try {
      const response = await fetch('http://localhost:8080/api/v1/user/all', {
        method: 'GET', // Assuming you are fetching data, change as necessary
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${sessionStorage.getItem('token')}` // Include the token as a Bearer token
        }
      });
      if (response.ok) {
        const data = await response.json();
        setDonors(data);
      } else {
        console.error('Failed to fetch donors:', response.status);
      }
    } catch (error) {
      console.error('Error fetching donors:', error);
    }
  };

  const fetchDonationCenters = async () => {
    try {
      const response = await fetch('http://localhost:8080/api/v1/dc/all', {
        method: 'GET', // Assuming you are fetching data, change as necessary
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${sessionStorage.getItem('token')}` // Include the token as a Bearer token
        }
      });
      if (response.ok) {
        const data = await response.json();
        setDonationCenters(data);
      } else {
        console.error('Failed to fetch donation centers:', response.status);
      }
    } catch (error) {
      console.error('Error fetching donation centers:', error);
    }
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    console.log(value);
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch('http://localhost:8080/api/v1/dr/create', {
        method: 'POST', // Assuming you are fetching data, change as necessary
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${sessionStorage.getItem('token')}` // Include the token as a Bearer token
        },
        body: JSON.stringify({
          userId: formData.donorId,
          donationCenterId: formData.donationCenterId,
          status: 'PENDING'
        })
      });
      if (response.ok) {
        const data = await response.json();
        console.log(data);
      } else {
        console.error('Failed to fetch donation centers:', response.status);
      }
    } catch (error) {
      console.error('Error fetching donation centers:', error);
    }

    // Reset form data after submission
    setFormData({
      donorId: '',
      donationCenterId: '',
    });
  };

  return (
    <>

    <div className="background-container-donation-1">
    <div className="call-registration-form-container">
      <h2>Call Registration Form</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="donorName">Donor Name:</label>
          <select
            name="donorId"
            id="donorId"
            value={formData.donorId}
            onChange={handleFormChange}
            required
          >
            <option value="">Select Donor</option>
            {donors.map((donor) => (
              <option key={donor.id} value={donor.id}>{donor.name}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="donationCenter">Donation Center:</label>
          <select
            name="donationCenterId"
            id="donationCenterId"
            value={formData.donationCenterId}
            onChange={handleFormChange}
            required
          >
            <option value="">Select Donation Center</option>
            {donationCenters.map((center) => (
              <option key={center.id} value={center.id}>{center.name} - {center.city}</option>
            ))}
          </select>
        </div>
        
        
        <button type="submit">Register Call</button>
      </form>
    </div>
    </div>
    </>
  );
};

export default CallRegistrationSystem;
