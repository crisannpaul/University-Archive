import React, { useEffect, useState } from 'react';
import { GoogleMap, LoadScript, Marker } from '@react-google-maps/api';


const mapContainerStyle = {
    position: 'absolute',
    top: 0,
    left: '21%',
    width: '80%',
    height: '100%',
    
};

const defaultCenter = {
    lat: 46.7712, 
    lng: 23.6236
};

const DonationCentersMap = () => {
    const [donationCenters, setDonationCenters] = useState([]);

    useEffect(() => {
        const fetchDonationCenters = async () => {
            try {
                const response = await fetch('http://localhost:8080/api/v1/dc/all', {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${sessionStorage.getItem('token')}`
                    }
                });
                if (response.ok) {
                    const data = await response.json();
                    setDonationCenters(data);
                    console.lof(data)
                } else {
                    console.error('Failed to fetch donation centers');
                }
            } catch (error) {
                console.error('Error fetching donation centers:', error);
            }
        };

        fetchDonationCenters();
    }, []);

    return (
        <div className="donation-centers-map">
            <LoadScript googleMapsApiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY}>
                <GoogleMap
                    mapContainerStyle={mapContainerStyle}
                    center={defaultCenter}
                    zoom={8}
                >
                    {donationCenters.map(center => {
                        console.log('Center:', center);
                        console.log('Latitude:', center.latitude, 'Longitude:', center.longitude);
    return (
        <Marker
            key={center.id}
            position={{ lat: center.latitude, lng: center.longitude }}
            title={center.name}
        />
    );
})}

                </GoogleMap>
            </LoadScript>
        </div>
    );
};

export default DonationCentersMap;
