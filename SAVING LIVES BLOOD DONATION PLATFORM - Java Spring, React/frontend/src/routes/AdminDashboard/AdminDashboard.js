import React from 'react';
import {useNavigate} from 'react-router-dom';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const navigate = useNavigate();

  const handleNavigation = (path) => {
    navigate(path);
  };

  return (
    <>
      <div className="background-dash-admin"></div>
      <div className="dashboard">
        <div className="element" onClick={() => handleNavigation('/DonationCenter')}>
          <h2>Add Donation Centers</h2>
          <p>Register new donation centers here.</p>
        </div>
        <div className="element" onClick={() => handleNavigation('/AdminRequirements')}>
          <h2>Add Donation Requirements</h2>
          <p>Specify new donation requirements here.</p>
        </div>
        <div className="element" onClick={() => handleNavigation('/post-interactive-content')}>
          <h2>Post Interactive Content</h2>
          <p>Create posts for doctors and users.</p>
        </div>
        <div className="element" onClick={() => handleNavigation('/RegisterDoctor')}>
          <h2>Doctor register</h2>
          <p>Register a doctor.</p>
        </div>
      </div>
    </>
  );
};

export default AdminDashboard;
