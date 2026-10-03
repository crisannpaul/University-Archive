import React from 'react'
import {BrowserRouter as Router, Route, Switch} from 'react-router-dom'
import NavigationBar from './navigation-bar'
import Home from './home/home';
import AdminPage from './person/admin-page'
import LoginPage from './login/login-page';
import ErrorPage from './commons/errorhandling/error-page';
import styles from './commons/styles/project-style.css';
import RegisterPage from './register/register-page';
import UserPage from './user/user-page';

const localStorage = window.localStorage;
localStorage.setItem("role", "")

class App extends React.Component {


    render() {

        return (
            <div className={styles.back}>
            <Router>
                <div>
                    <NavigationBar />
                    <Switch>
                        
                        <Route
                            exact
                            path='/'
                            render={() => <Home/>}
                        />

                        <Route
                            exact
                            path='/login'
                            render={() => <LoginPage/>}
                        />

                        <Route
                            exact
                            path='/register'
                            render={() => <RegisterPage/>}
                        />

                        <Route
                            exact
                            path='/user'
                            render={() => <UserPage/>}
                        />

                        <Route
                            exact
                            path='/admin'
                            render={() => <AdminPage/>}
                        />

                        {/*Error*/}
                        <Route
                            exact
                            path='/error'
                            render={() => <ErrorPage/>}
                        />

                        <Route render={() =><ErrorPage/>} />
                    </Switch>
                </div>
            </Router>
            </div>
        )
    };
}

export default App
