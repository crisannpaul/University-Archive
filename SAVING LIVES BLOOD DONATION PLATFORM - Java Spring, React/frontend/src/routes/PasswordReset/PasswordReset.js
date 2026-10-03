import React, {useState} from 'react';
import './PasswordReset.css';

const PasswordReset = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [message, setMessage] = useState('');

    const handleEmailChange = (event) => {
        setEmail(event.target.value);
    };

    const handlePasswordChange = (event) => {
        setPassword(event.target.value);
    };

    const handleConfirmPasswordChange = (event) => {
        setConfirmPassword(event.target.value);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (password !== confirmPassword) {
            setMessage('Passwords do not match.');
            return;
        }
        try {
            // Placeholder for backend API call
            await resetPassword(email, password);
            setMessage('Your password has been reset successfully. Please login with your new password.');
            setEmail('');
            setPassword('');
            setConfirmPassword('');
        } catch (error) {
            setMessage('Failed to reset password. Please try again later.');
        }
    };

    // Placeholder function to simulate backend password reset
    const resetPassword = (email, password) => {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                if (email && password) {
                    resolve();
                } else {
                    reject();
                }
            }, 1000);
        });
    };

    return (
        <>

        <div className="background-image-3">
            <div className="password-reset-form">
                <h2 className="custom-text-component">Reset Your Password</h2>
                <form onSubmit={handleSubmit} className="form">
                    <input
                        type="email"
                        placeholder="Email Address"
                        value={email}
                        onChange={handleEmailChange}
                        className="input"
                        required
                    />
                    <input
                        type="password"
                        placeholder="New Password"
                        value={password}
                        onChange={handlePasswordChange}
                        className="input"
                        required
                    />

                    <input
                        type="password"
                        placeholder="Confirm Password"
                        value={confirmPassword}
                        onChange={handleConfirmPasswordChange}
                        className="input"
                        required
                    />
                    <div className="button-container">
                        <button type="submit">Reset Password</button>
                    </div>

                </form>
                {message && <p className="success-message">{message}</p>}
            </div>
        </div>
        </>
    );
};

export default PasswordReset;
