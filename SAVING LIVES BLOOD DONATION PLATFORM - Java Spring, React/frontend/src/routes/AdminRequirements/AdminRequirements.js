import React, {useState} from 'react';
import './AdminRequirements.css';

const AdminRequirements = () => {
    const [requirements, setRequirements] = useState({
        age: '',
        weight: '',
        healthConditions: ''
    });

    const handleChange = (event) => {
        const { name, value } = event.target;
        setRequirements(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (event) => {
        event.preventDefault();

        try {
            const response = await fetch('http://localhost:8080/api/v1/requirements', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${sessionStorage.getItem('token')}`
                },
                body: JSON.stringify(requirements)
            });

            if (response.ok) {
                const data = await response.json();
                console.log('Requirements updated successfully:', data);
            } else {
                console.error('Failed to update requirements:', response.status);
            }
        } catch (error) {
            console.error('Error submitting form:', error);
        }
    };

    return (
        <>

            <div className="background-container-requirements">
                <div className="admin-requirements-container">
                    <form onSubmit={handleSubmit}>
                        <label htmlFor="age">Minimum Age</label>
                        <input
                            type="number"
                            id="age"
                            name="age"
                            value={requirements.age}
                            onChange={handleChange}
                            required
                        />

                        <label htmlFor="weight">Minimum Weight (kg)</label>
                        <input
                            type="number"
                            id="weight"
                            name="weight"
                            value={requirements.weight}
                            onChange={handleChange}
                            required
                        />

                        <label htmlFor="healthConditions">Health Conditions</label>
                        <textarea
                            id="healthConditions"
                            name="healthConditions"
                            value={requirements.healthConditions}
                            onChange={handleChange}
                            required
                        />

                        <button type="submit">Update Requirements</button>
                    </form>
                </div>
            </div>
        </>
    );
};

export default AdminRequirements;
