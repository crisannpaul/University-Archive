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

      <div className="background-dash-user"></div>
      <div className="dashboard">
        <div className="element" onClick={() => handleNavigation('/add-donation-center')}>
          <h2>Add Donation Centers</h2>
          <p>Register new donation centers here.</p>
        </div>
        <div className="element" onClick={() => handleNavigation('/add-donation-requirements')}>
          <h2>Add Donation Requirements</h2>
          <p>Specify new donation requirements here.</p>
        </div>
        <div className="element" onClick={() => handleNavigation('/post-interactive-content')}>
          <h2>Post Interactive Content</h2>
          <p>Create posts for doctors and users with title and description.</p>
        </div>
      </div>
    </>
  );
};

export default AdminDashboard;
