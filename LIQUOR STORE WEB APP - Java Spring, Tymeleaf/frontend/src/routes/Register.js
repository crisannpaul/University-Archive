
import React , {useState} from "react"
import Navbar from "../components/Navbar";
import "./RegisterStyles.css"
function Register (props)
{

    const [email, setEmail] = useState('');
    const [pass, setPass] = useState('');
    const [name, setName] = useState('');

    const handleSubmit = (e) =>
    {
        e.preventDefault();
        console.log(email);
    }
    return (
        <>
            <Navbar />
            <div className="register-form-container">
            
            <form className = "register-form" onSubmit={handleSubmit}>
                <h2>Register</h2>
                <label htmlFor="name">full name</label>
                <input value= {name} onChange={(e) => setName(e.target.value)} type="name" placeholder="full name"/>
                <label htmlFor="email">email</label>
                <input value= {email} onChange={(e) => setEmail(e.target.value)} type= "email"placeholder="youremail"/>
                <label htmlFor="password">password</label>
                <input value= {pass} onChange={(e) => setPass(e.target.value)} type= "pass"placeholder="**********"/>
                <button type="submit">Register</button>
            </form>
            <a href="/signup"><button className="link-btn-login">Already have an account? Log in here.</button></a>
            </div>
        </>
    );
}
export default Register;