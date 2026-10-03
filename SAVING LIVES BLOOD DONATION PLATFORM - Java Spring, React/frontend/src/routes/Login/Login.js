import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css'; 

function LoginForm() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        const loginData = {
            email: email,
            password: password
        };

        try {
            const response = await fetch('http://localhost:8080/api/v1/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(loginData)
            });

            if (response.ok) {
                const result = await response.json();

                console.log('Login successful:', result);
                sessionStorage.setItem('token', result.token);
                sessionStorage.setItem('id', result.id)
                sessionStorage.setItem('role', result.role)
                alert('Logged in successfully!');
                if (result.role === "USER") {
                    if (result.bloodGroup !== 'null' && result.weight !== 'null' && result.age !== 'null') {
                        navigate('/userdashboard');
                    } else {
                        navigate('/ConfigureUserProfile')
                    }
                }
                if (result.role === "ADMIN") {
                    navigate('/admindashboard')
                }
                if (result.role === "DOCTOR") {
                    navigate("/doctorDashboard")
                }
            } else {
                console.log('Login attempt failed:', response.status);
                alert('Login failed. Please check your email and password.');
            }
        } catch (error) {
            console.error('Login failed:', error);
            alert('An error occurred during login. Please try again later.');
        }
    };

    return (
        <>
        <div className="background-image-3">
            <div className="login-form">

                <h2 className="custom-text-component">Login</h2>

                <form onSubmit={handleSubmit} className="form">
                    
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
                        <button type="submit">Login</button>
                    </div>

                </form>
                <p></p>
                
                <a href="/register" style={{ color: "white" }}>
                 Don't have an account? 
                 Register here.
                </a>
                
            </div>
        </div>
        </>
    );
}

export default LoginForm;
