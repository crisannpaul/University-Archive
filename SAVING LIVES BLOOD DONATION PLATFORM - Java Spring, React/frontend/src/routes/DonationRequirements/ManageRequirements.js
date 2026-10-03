import React, {useEffect, useState} from 'react';
import './ManageRequirements.css';

const ManageRequirements = () => {
    const [newCondition, setNewCondition] = useState('');
    const [conditions, setConditions] = useState([]);
    const [minAge, setMinAge] = useState('');
    const [maxAge, setMaxAge] = useState('');
    const [minWeight, setMinWeight] = useState('');
    const [maxWeight, setMaxWeight] = useState('');
    const [message, setMessage] = useState('');

    useEffect(() => {
        fetchRequirements();
    }, []);

    const fetchRequirements = async () => {
        try {
            const response = await fetch('http://localhost:8080/api/v1/requirements');
            const data = await response.json();
            setConditions(data.conditions);
            setMinAge(data.minAge);
            setMaxAge(data.maxAge);
            setMinWeight(data.minWeight);
            setMaxWeight(data.maxWeight);
        } catch (error) {
            console.error('Error fetching requirements:', error);
        }
    };

    const handleAddCondition = async (e) => {
        e.preventDefault();

        const newConditionData = {
            name: newCondition
        };

        try {
            const response = await fetch('http://localhost:8080/api/v1/requirements', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(newConditionData),
            });

            if (response.ok) {
                setMessage('Condition added successfully!');
                setNewCondition('');
                fetchRequirements();
            } else {
                setMessage('Failed to add condition.');
            }
        } catch (error) {
            console.error('Error adding condition:', error);
            setMessage('An error occurred.');
        }
    };

    const handleUpdateRequirements = async (e) => {
        e.preventDefault();

        const requirementsData = {
            minAge,
            maxAge,
            minWeight,
            maxWeight,
            conditions
        };

        try {
            const response = await fetch('http://localhost:8080/api/v1/requirements', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requirementsData),
            });

            if (response.ok) {
                setMessage('Requirements updated successfully!');
            } else {
                setMessage('Failed to update requirements.');
            }
        } catch (error) {
            console.error('Error updating requirements:', error);
            setMessage('An error occurred.');
        }
    };

    const handleDeleteCondition = async (id) => {
        try {
            const response = await fetch(`http://localhost:8080/api/v1/requirements/${id}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                setMessage('Condition deleted successfully!');
                fetchRequirements();
            } else {
                setMessage('Failed to delete condition.');
            }
        } catch (error) {
            console.error('Error deleting condition:', error);
            setMessage('An error occurred.');
        }
    };

    return (
        <div className="manage-requirements-container">
            <h2>Manage Donation Requirements</h2>
            <form onSubmit={handleUpdateRequirements} className="requirements-form">
                <label>
                    Minimum Age:
                    <input
                        type="number"
                        value={minAge}
                        onChange={(e) => setMinAge(e.target.value)}
                        required
                        className="input"
                    />
                </label>
                <label>
                    Maximum Age:
                    <input
                        type="number"
                        value={maxAge}
                        onChange={(e) => setMaxAge(e.target.value)}
                        required
                        className="input"
                    />
                </label>
                <label>
                    Minimum Weight (kg):
                    <input
                        type="number"
                        value={minWeight}
                        onChange={(e) => setMinWeight(e.target.value)}
                        required
                        className="input"
                    />
                </label>
                <label>
                    Maximum Weight (kg):
                    <input
                        type="number"
                        value={maxWeight}
                        onChange={(e) => setMaxWeight(e.target.value)}
                        required
                        className="input"
                    />
                </label>
                <button type="submit">Update Requirements</button>
            </form>
            {message && <p className="message">{message}</p>}
            <form onSubmit={handleAddCondition} className="requirements-form">
                <label>
                    Add New Condition:
                    <input
                        type="text"
                        placeholder="Condition"
                        value={newCondition}
                        onChange={(e) => setNewCondition(e.target.value)}
                        required
                        className="input"
                    />
                </label>
                <button type="submit">Add Condition</button>
            </form>
            {message && <p className="message">{message}</p>}
            <h3>Existing Conditions</h3>
            <ul className="conditions-list">
                {conditions.map(condition => (
                    <li key={condition.id}>
                        {condition.name}
                        <button onClick={() => handleDeleteCondition(condition.id)}>Delete</button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default ManageRequirements;
