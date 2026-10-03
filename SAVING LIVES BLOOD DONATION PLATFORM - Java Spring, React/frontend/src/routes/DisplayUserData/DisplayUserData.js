import React, {useEffect, useState} from 'react';
import './DisplayUserData.css';

const UserProfile = () => {
  // Sample user data (to be replaced with data fetched from the database)
  const [userData, setUserData] = useState(null);
  const userId = sessionStorage.getItem('id')

  // State to manage visibility of donation history
  const [showDonationHistory, setShowDonationHistory] = useState(false);

  // Sample hardcoded donation history
  const donationHistory = [
    { id: 1, date: '2024-05-01' },
    { id: 2, date: '2024-04-15' },
    { id: 3, date: '2024-03-28' }
  ];

  // Function to handle button click to show donation history
  const handleShowDonationHistory = () => {
    setShowDonationHistory(true);
    // document.querySelector('.background-container').classList.add('blur-background');
  };

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await fetch(`http://localhost:8080/api/v1/user/get?userId=${userId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          setUserData({
            name: data.name,
            email: data.email,
            bloodGroup: data.bloodGroup,
            weight: `${data.weight} kg`,
            age: `${data.age} years`,
            city: data.city
          });
        } else {
          console.error('Failed to fetch user data:', response.status);
          alert('Failed to load user data.');
        }
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    };

    fetchUserData();
  }, []);

  if (!userData) {
    return <div>Loading...</div>;
  }

  return (
      <>
    <div className="background-container-data-view">
    <div className="user-profile-container">
      <h2>User Profile</h2>
      <div className="user-details">
        <div>
          <strong>Name:</strong> {userData.name}
        </div>
        <div>
          <strong>Email:</strong> {userData.email}
        </div>
        <div>
          <strong>Phone:</strong> {userData.phone}
        </div>
        <div>
          <strong>Blood Group:</strong> {userData.bloodGroup}
        </div>
        <div>
          <strong>Weight:</strong> {userData.weight}
        </div>
        <div>
          <strong>Age:</strong> {userData.age}
        </div>
      </div>
      <button className="toggle-button" onClick={handleShowDonationHistory}>Show Donation History</button>
      {showDonationHistory && (
        <div className="donation-history-container">
          <h2>Donation History</h2>
          <ul>
            {donationHistory.map((donation, index) => (
              <li key={index}>
                Donation ID: {donation.id} - Date: {donation.date}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
    </div>
    </>
  );
};

export default UserProfile;
