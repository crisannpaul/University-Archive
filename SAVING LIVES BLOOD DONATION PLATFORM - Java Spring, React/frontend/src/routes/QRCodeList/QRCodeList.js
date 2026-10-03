import React, { useEffect, useState } from 'react';

const QRCodeList = ({ userID }) => {
  const [qrCodes, setQRCodes] = useState([]);

  useEffect(() => {
    fetchQRCodes();
  }, []);

  const fetchQRCodes = async () => {
    try {
      const response = await fetch(`http://localhost:8080/api/v1/qrcode/get/${userID}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setQRCodes(data);
      } else {
        console.error('Failed to fetch QR codes:', response.status);
      }
    } catch (error) {
      console.error('Error fetching QR codes:', error);
    }
  };

  return (
    <div className="qr-code-list">
      <h2>QR Codes</h2>
      <div className="qr-codes">
        {qrCodes.map((qr) => (
          <div key={qr.id} className="qr-code-item">
            <h4>{qr.title}</h4>
            <img src={qr.qr_sting} alt={`QR code for ${qr.title}`} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default QRCodeList;
