import React, {useState} from 'react';
import './ConfigureUserProfile.css';
import {useNavigate} from "react-router-dom";


const ProfileConfigForm = () => {
  const [bloodGroup, setBloodGroup] = useState('');
  const [weight, setWeight] = useState('');
  const [age, setAge] = useState('');
  const [city, setCity] = useState('');
  const navigate = useNavigate();


  const handleSubmit = async (e) => {
    e.preventDefault();

    const profileData = {
      id: sessionStorage.getItem('id'),
      bloodGroup: bloodGroup,
      weight: weight,
      age: age,
      city: city
    };

    console.log(profileData)

    try {
      const response = await fetch('http://localhost:8080/api/v1/user/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
        body: JSON.stringify(profileData)
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Profile update successful:', result);

        navigate('/userdashboard'); ///////////////////
      } else {
        console.error('Failed to update profile:', response.status);
      }
    } catch (error) {
      console.error('Error submitting profile data:', error);
    }
  };


  return (
    <>

    <div className="background-container-profile-configuration">
    <div className="profile-config-form-container">

      <h2>Profile Configuration</h2>
      <form onSubmit={handleSubmit}>

        <label>
          Blood Group:
          <input
            type="text"
            value={bloodGroup}
            onChange={(e) => setBloodGroup(e.target.value)}
            required
            className="inputConfiguration"
          />
        </label>

        <label>
          Weight (kg):
          <input
            type="number"
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
            required
            className="inputConfiguration" 
          />
        </label>

        <label>
          Age:
          <input
            type="number"
            value={age}
            onChange={(e) => setAge(e.target.value)}
            required
            className="inputConfiguration"
          />
        </label>

        <label>
          City:
          <input
            type="text"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            required
            className="inputConfiguration"
          />
        </label>

        <button type="submit">Save</button>
      </form>
    </div>
    
    </div>
    </>
  );
};

export default ProfileConfigForm;
