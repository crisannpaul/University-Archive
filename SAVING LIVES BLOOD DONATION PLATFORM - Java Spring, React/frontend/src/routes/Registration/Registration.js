import React, { useState } from 'react';
import './Registration.css';
import { useNavigate } from 'react-router-dom';

function RegistrationForm() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        const registrationData = {
            name: name,
            email: email,
            password: password
        };

        try {
            const response = await fetch('http://localhost:8080/api/v1/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(registrationData)
            });

            if (response.ok) {
                const result = await response.json();
                console.log('Registration successful:', result);
                setName('');
                setEmail('');
                setPassword('');
                navigate('/Login'); ///////////////////////////////
            } else {
                console.error('Registration failed:', response.status);
            }
        } catch (error) {
            console.error('There was a problem:', error);
        }
    };

    return (
        <>
            <div className="background-image-5">
                <div className="register-form">
                    <h2 className="custom-text-component">Register</h2>
                    <form onSubmit={handleSubmit} className="form">
                        <input
                            type="name"
                            placeholder="Name"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            className="input"
                            required
                        />
                        <input
                            type="email"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="input"
                            required
                        />
                        <input
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="input"
                            required
                        />
                        <div className="button-container">
                            <button type="submit">Register</button>
                        </div>
                    </form>
                    <p></p>
                    <a href="/Login" style={{ color: "white" }}>
                        Already have an account?
                        Go to login.
                    </a>
                </div>
            </div>
        </>
    );
}

export default RegistrationForm;
