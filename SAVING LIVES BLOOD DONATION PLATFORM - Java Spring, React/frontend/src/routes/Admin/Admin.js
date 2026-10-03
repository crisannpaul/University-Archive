import React, {useEffect, useState} from 'react';
import './Admin.css';
import {useNavigate} from 'react-router-dom';

const Admin = () => {
    const [posts, setPosts] = useState([]);
    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [editId, setEditId] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        fetchPosts();
    }, []);

    const fetchPosts = async () => {
        try {
            const response = await fetch('http://localhost:8080/api/v1/posts');
            const data = await response.json();
            setPosts(data);
        } catch (error) {
            console.error('Error fetching posts:', error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        const postData = { title, content };

        try {
            if (editId) {
                await fetch(`http://localhost:8080/api/v1/posts/${editId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(postData),
                });
            } else {
                await fetch('http://localhost:8080/api/v1/posts', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(postData),
                });
            }
            setTitle('');
            setContent('');
            setEditId(null);
            await fetchPosts();
        } catch (error) {
            console.error('Error submitting post:', error);
        }
    };

    const handleEdit = (post) => {
        setTitle(post.title);
        setContent(post.content);
        setEditId(post.id);
    };

    const handleDelete = async (id) => {
        try {
            await fetch(`http://localhost:8080/api/v1/posts/${id}`, {
                method: 'DELETE',
            });
            await fetchPosts();
        } catch (error) {
            console.error('Error deleting post:', error);
        }
    };

    return (
        <div className="admin-container">
            <div className="form-container">
                <h2>{editId ? 'Edit Post' : 'Create Post'}</h2>
                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        placeholder="Title"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        required
                        className="input"
                    />
                    <textarea
                        placeholder="Content"
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        required
                        className="input"
                    ></textarea>
                    <button type="submit">{editId ? 'Update' : 'Create'}</button>
                </form>
            </div>
            <div className="posts-list">
                <h2>Existing Posts</h2>
                {posts.map((post) => (
                    <div key={post.id} className="post-item">
                        <h3>{post.title}</h3>
                        <p>{post.content}</p>
                        <button onClick={() => handleEdit(post)}>Edit</button>
                        <button onClick={() => handleDelete(post.id)}>Delete</button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Admin;
