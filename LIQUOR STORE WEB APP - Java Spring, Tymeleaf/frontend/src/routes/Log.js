import React, {useState} from "react";
import Login from "./Login"
import Register from "./Register";

function Log () {
    const [currentForm, setCurrentForm] = useState('login');

    const toggleForm = (formName) => {
        setCurrentForm(formName);
    }
    return (
        <div className="Log">
        currentForm === "login" ? <Login /> : <Register  />
        </div>
    )
}
export default Log;