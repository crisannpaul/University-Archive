import React, {useState} from 'react';
import './PostInteractiveContent.css';

const PostInteractiveContent = () => {
  const [formData, setFormData] = useState({
    title: '',
    description: ''
  });

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      console.log(formData);
      const response = await fetch('http://localhost:8080/api/v1/infoContent/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        console.log('Content posted successfully');
        setFormData({ title: '', description: '' }); // Clear the form
      } else {
        console.error('Failed to post content:', response.status);
      }
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  return (
    <>
      <div className="interactive-content-background"></div>
      <div className="content-form-container">
        <h2>Post Interactive Content</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="title">Title:</label>
            <input
              type="text"
              name="title"
              id="title"
              value={formData.title}
              onChange={handleFormChange}
              required
              className="post-input"
            />
          </div>
          <div className="form-group">
            <label htmlFor="description">Description:</label>
            <textarea
              name="description"
              id="description"
              value={formData.description}
              onChange={handleFormChange}
              required
              className="post-input"
            />
          </div>
          <button type="submit" className="submit-button">Post Content</button>
        </form>
      </div>
    </>
  );
};

export default PostInteractiveContent;
