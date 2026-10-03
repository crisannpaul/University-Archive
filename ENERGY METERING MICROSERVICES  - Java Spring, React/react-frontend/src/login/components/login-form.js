import React from 'react';
import validate from "./validators/login-validator";
import Button from "react-bootstrap/Button";
import * as API_LOGIN from "../api/login-api";
import APIResponseErrorMessage from "../../commons/errorhandling/api-response-error-message";
import {Col, Row} from "reactstrap";
import { FormGroup, Input, Label} from 'reactstrap';
import { Redirect } from 'react-router-dom';
import {decodeToken} from "../../commons/api/jwtDecoder";
import { useHistory } from 'react-router-dom';

const localStorage = window.localStorage;

class LoginForm extends React.Component {
    
    constructor(props) {
        super(props);
        this.toggleForm = this.toggleForm.bind(this);

        this.state = {

            errorStatus: 0,
            error: null,
            isUserLoaded: false,
            formIsValid: false,

            formControls: {
                userName: {
                    value: '',
                    placeholder: '...',
                    valid: false,
                    touched: false,
                    validationRules: {
                        minLength: 3,
                        isRequired: true
                    }
                },
                password: {
                    value: '',
                    placeholder: '...',
                    valid: false,
                    touched: false,
                    validationRules: {
                        minLength: 4,
                        isRequired: true
                    }
                },
            }
        };

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    toggleForm() {
        this.setState({collapseForm: !this.state.collapseForm});
    }


    handleChange = event => {

        const name = event.target.name;
        const value = event.target.value;

        const updatedControls = this.state.formControls;

        const updatedFormElement = updatedControls[name];

        updatedFormElement.value = value;
        updatedFormElement.touched = true;
        updatedFormElement.valid = validate(value, updatedFormElement.validationRules);
        updatedControls[name] = updatedFormElement;

        let formIsValid = true;
        for (let updatedFormElementName in updatedControls) {
            formIsValid = updatedControls[updatedFormElementName].valid && formIsValid;
        }

        this.setState({
            formControls: updatedControls,
            formIsValid: formIsValid
        });

    };

    authenticateUser(user) {
        return API_LOGIN.postLogin(user, (result, status, error) => {
            if (result !== null && (status === 200 || status === 201)) {
                console.log("Successfully authenticated user with id: " + result);

                // Store the entire JWT token
                localStorage.setItem("jwt", result.token);

                // Decode the token to extract user details
                const decodedToken = decodeToken(result.token);
                localStorage.setItem("id", decodedToken.id);
                localStorage.setItem("username", decodedToken.sub);
                localStorage.setItem("role", decodedToken.role);
                this.setState(({
                    isUserLoaded: true
                }));
                console.log(localStorage);

            } else {
                console.log(error)
                this.setState(({
                    errorStatus: status,
                    error: error
                }));
            }
        });
    }

    handleSubmit() {
        let user = {
            username: this.state.formControls.userName.value,
            password: this.state.formControls.password.value,
        };

        console.log(user);
        this.authenticateUser(user);
    }

    render() {
        return (
            
            <div>
                {this.state.isUserLoaded && localStorage.role === "ROLE_ADMIN" && <Redirect to="/admin" push/>}
                {this.state.isUserLoaded && localStorage.role === "ROLE_CLIENT" && <Redirect to="/user" push/>}

                <FormGroup id='userName'>
                    <Label for='userNameField'> Username: </Label>
                    <Input name='userName' id='userNameField' placeholder={this.state.formControls.userName.placeholder}
                           onChange={this.handleChange}
                           defaultValue={this.state.formControls.userName.value}
                           touched={this.state.formControls.userName.touched? 1 : 0}
                           valid={this.state.formControls.userName.valid}
                           required
                    />
                    {this.state.formControls.userName.touched && !this.state.formControls.userName.valid &&
                    <div className={"error-message row"}> * Username must have at least 3 characters </div>}
                </FormGroup>

                <FormGroup id='password'>
                    <Label for='passwordField'> Password: </Label>
                    <Input name='password' id='passwordField' placeholder={this.state.formControls.password.placeholder}
                           type='password'
                           onChange={this.handleChange}
                           defaultValue={this.state.formControls.password.value}
                           touched={this.state.formControls.password.touched? 1 : 0}
                           valid={this.state.formControls.password.valid}
                           required
                    />
                    {this.state.formControls.password.touched && !this.state.formControls.password.valid &&
                    <div className={"error-message"}> * Passowrd must be at least 4 characters long</div>}
                </FormGroup>

                    <Row>
                        <Col sm={{size: '4', offset: 2}}>
                            <Button type={"submit"} disabled={!this.state.formIsValid} onClick={this.handleSubmit}>  Login </Button>
                        </Col>
                    </Row>

                {
                    this.state.errorStatus > 0 &&
                    <APIResponseErrorMessage errorStatus={this.state.errorStatus} error={this.state.error}/>
                }
            </div>
        ) ;
    }
}

export default LoginForm;