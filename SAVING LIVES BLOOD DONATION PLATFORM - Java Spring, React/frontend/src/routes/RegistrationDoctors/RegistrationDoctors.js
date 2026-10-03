import React, {useState} from 'react';
import CallRegistrationForm from '../DonationCalls/DonationCalls';


const CallRegistrationSystem = () => {
  const [callLogs, setCallLogs] = useState([]);

  const handleCallRegister = (callData) => {
    setCallLogs([...callLogs, callData]);
  };

  return (
    <div className="call-registration-system-container">
      <CallRegistrationForm onCallRegister={handleCallRegister} />
      <div className="call-logs-container">
        <h2>Call Logs</h2>
        <ul>
          {callLogs.map((call, index) => (
            <li key={index}>
              <strong>Donor Name:</strong> {call.donorName},{' '}
              <strong>Outcome:</strong> {call.outcome}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default CallRegistrationSystem;
