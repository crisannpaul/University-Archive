import React, {useState} from "react";
import Navbar from "../components/Navbar";
import "./LoginStyles.css"


function Login (props)
{
    
    const[email, setEmail  ] = useState('');
    const[pass, setPass] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log(email);
    }
    return(
        <>
            <Navbar />
        
            <div className="auth-form-container">
                
            <form className = "login-form" onSubmit={handleSubmit}>
                <h2>Log in</h2>
                <label for= "email">email</label>
                <input value={email} onChange={(e) => setEmail(e.target.value)}type = "email" placeholder="youremail.com" id="email" name = "email"/>
                <label for="password">password</label>
                <input value = {pass} onChange={(e) => setPass(e.target.value)}type="password" placeholder="****" id="password" name = "password"/>
                <button type="submit">Log In</button>
            </form>
            <a href="/register"><button className="link-btn">You don't have an account? Register here</button></a>
            
            </div>
            
        </>

    );
    
}

export default Login;