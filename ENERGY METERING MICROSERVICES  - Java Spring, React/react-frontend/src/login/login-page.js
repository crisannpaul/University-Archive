import React from 'react';
import LoginForm from "./components/login-form";

const localStorage = window.localStorage;
localStorage.setItem("role", "")

class LoginPage extends React.Component {
    render() {
        return (
            <LoginForm/>
        )
    }
}

export default LoginPage;