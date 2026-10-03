import React, { useState, useEffect } from 'react';
import DonationCentersMap from '../DonationCenterMap/DonationCenterMap';
import './RegisterDonationForm.css';

const DonationCenterForm = () => {
    const [formData, setFormData] = useState({
        name: '',
        country: '',
        region: '',
        city: '',
        street: '',
        streetNumber: '',
        latitude: '',
        longitude: '',
    });

    const [role, setRole] = useState(sessionStorage.getItem('role'));

    const handleFormChange = (e) => {
        const { name, value } = e.target;
        console.log(name + " " + value);
        setFormData({
            ...formData,
            [name]: value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log("Form submitted");

        try {
            const response = await fetch('http://localhost:8080/api/v1/dc/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${sessionStorage.getItem('token')}`
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                const id = await response.json();
                console.log('Donation Center Registered with ID:', id);
            } else {
                console.error('Registration failed with status:', response.status);
            }
        } catch (error) {
            console.error('Error submitting form:', error);
        }
    };

    // Conditionally render the form based on role
    return (
        <>
        {role === 'USER' ? (
            <div className="map-container">
                <DonationCentersMap />
            </div>
        ) : (
            <div className="background-image-container">
                <div className="container">
                    <div className="form-container-donation">
                        <h2 className="form-heading">Register Donation Center</h2>
                        <form onSubmit={handleSubmit}>
                            <input
                                type="text"
                                name="name"
                                placeholder="Donation Center Name"
                                value={formData.name}
                                onChange={handleFormChange}
                                required
                                className="input-donation"
                            />
                            <input
                                type="text"
                                name="country"
                                placeholder="Country"
                                value={formData.country}
                                onChange={handleFormChange}
                                required
                                className="input-donation"
                            />
                            <input
                                type="text"
                                name="region"
                                placeholder="Region"
                                value={formData.region}
                                onChange={handleFormChange}
                                className="input-donation"
                            />
                            <input
                                type="text"
                                name="city"
                                placeholder="City"
                                value={formData.city}
                                onChange={handleFormChange}
                                required
                                className="input-donation"
                            />
                            <input
                                type="text"
                                name="street"
                                placeholder="Street"
                                value={formData.street}
                                onChange={handleFormChange}
                                required
                                className="input-donation"
                            />
                            <input
                                type="text"
                                name="streetNumber"
                                placeholder="Street Number"
                                value={formData.streetNumber}
                                onChange={handleFormChange}
                                required
                                className="input-donation"
                            />
                            <input
                                type="text"
                                name="latitude"
                                placeholder="46.7712"
                                value={formData.latitude}
                                onChange={handleFormChange}
                                required
                                className="input-donation"
                            />
                            <input
                                type="text"
                                name="longitude"
                                placeholder="23.6236"
                                value={formData.longitude}
                                onChange={handleFormChange}
                                required
                                className="input-donation"
                            />
                            <p></p>
                            <button className="button-register" type="submit">Register</button>
                        </form>
                    </div>
                    <div className="map-container">
                        <DonationCentersMap/>
                    </div>
                </div>
            </div>
        )}
        </>
    );
};

export default DonationCenterForm;
