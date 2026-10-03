// Home.js
import React from 'react';
import {Link} from 'react-router-dom';
import './Home.css';

const Home = () => {
  return (
    <div className="background-image-home">
      <div className="home-container">
        <div className="home-content">
          <div className="home-links">
            <Link to="/register" className="login-link">You don't have an account? Register here.</Link>
            <Link to="/login" className="register-link">Already have an accont? Go to login.</Link>

          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
