import React, { useState, useEffect } from 'react';
import './RegisterDoctor.css';

const RegisterDoctor = () => {
    const [users, setUsers] = useState([]);
    const [selectedUser, setSelectedUser] = useState('');
    const [message, setMessage] = useState('');

    useEffect(() => {
        fetchUsers();
    }, []);

    const fetchUsers = async () => {
        try {
            const response = await fetch('http://localhost:8080/api/v1/user/all', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${sessionStorage.getItem('token')}`
                },
            });
            const data = await response.json();
            setUsers(data);
        } catch (error) {
            console.error('Error fetching users:', error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!selectedUser) {
            setMessage('Please select a user.');
            return;
        }

        try {
            const response = await fetch(`http://localhost:8080/api/v1/user/create_doctor/${selectedUser}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${sessionStorage.getItem('token')}`
                },
            });

            if (response.ok) {
                setMessage('Doctor registered successfully!');
                setSelectedUser('');
            } else if (response.status === 409) {
                setMessage('User is already a doctor.');
            } else {
                setMessage('Registration failed.');
            }
        } catch (error) {
            console.error('Error registering doctor:', error);
            setMessage('An error occurred.');
        }
    };

    return (
        <div className="register-doctor-container">
            <h2>Register Doctor</h2>
            <form onSubmit={handleSubmit} className="register-doctor-form">
                <label>
                    Select User:
                    <select
                        value={selectedUser}
                        onChange={(e) => setSelectedUser(e.target.value)}
                        required
                        className="input"
                    >
                        <option value="" disabled>Select a user</option>
                        {users.map(user => (
                            <option key={user.id} value={user.id}>
                                {user.firstName} {user.lastName} ({user.email})
                            </option>
                        ))}
                    </select>
                </label>
                <button type="submit" className="submit-button">Register</button>
            </form>
            {message && <p className="message">{message}</p>}
        </div>
    );
};

export default RegisterDoctor;
