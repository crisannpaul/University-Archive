import React, {useState} from 'react';
import './DonationCalls.css';

const CallRegistrationForm = ({ onCallRegister }) => {
  const [donorName, setDonorName] = useState('');
  const [outcome, setOutcome] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Pass the form data to the parent component
    onCallRegister({ donorName, outcome });
    // Reset form fields
    setDonorName('');
    setOutcome('');
  };

  return (
    <>
    <div className='background-container-donation'>
    <div className="call-registration-form-container">
      <h2>Register a Call</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Donor Name:
          <input
            type="text"
            value={donorName}
            onChange={(e) => setDonorName(e.target.value)}
            required
            className='input_donation'
          />
        </label>
        <label>
          Outcome:
          <select
            value={outcome}
            onChange={(e) => setOutcome(e.target.value)}
            required
          >
            <option value="">Select Outcome</option>
            <option value="successful">Successful</option>
            <option value="declined">Declined</option>
          </select>
        </label>
        <button type="submit">Register Call</button>
      </form>
    </div>
    </div>
    </>
  );
};

export default CallRegistrationForm;
