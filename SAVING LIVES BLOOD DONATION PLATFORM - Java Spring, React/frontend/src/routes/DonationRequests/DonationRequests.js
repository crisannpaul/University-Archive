import React, {useEffect, useState} from 'react';
import './DonationRequests.css';

const DonationRequests = () => {
    const [donationRequests, setDonationRequests] = useState([]);
    const userId = sessionStorage.getItem("id")

    useEffect(() => {
        fetchDonationRequests();
    }, []);

    const fetchDonationRequests = async () => {
        try {
            const response = await fetch(`http://localhost:8080/api/v1/dr/fetch-all/${userId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${sessionStorage.getItem('token')}`
                },
            });
            if (response.ok) {
                const data = await response.json();
                setDonationRequests(data);
            } else {
                console.error('Failed to fetch donation requests:', response.status);
            }
        } catch (error) {
            console.error('Error fetching donation requests:', error);
        }
    };

    const handleRequestClick = (id) => {
        console.log(`Selected donation request with ID ${id}`);
    };

    return (
        <>

            <div className="background-container-requests">
                <div className="donation-requests-container">
                    <ul>
                        {donationRequests.map((request) => (
                            <li key={request.id} onClick={() => handleRequestClick(request.id)} className="donation-request">
                                <div className="donation-request-info">
                                    <strong>Patient Name:</strong> {request.patientName}
                                </div>
                                <div className="donation-request-info">
                                    <strong>Blood Type:</strong> {request.bloodType}
                                </div>
                                <div className="donation-request-info">
                                    <strong>Date:</strong> {request.date}
                                </div>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </>
    );
};

export default DonationRequests;
