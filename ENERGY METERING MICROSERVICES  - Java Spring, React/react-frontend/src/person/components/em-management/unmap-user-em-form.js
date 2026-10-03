import React from 'react';
import validate from "../validators/user-validators";
import Button from "react-bootstrap/Button";
import * as API_EM_USER from "../../api/users-em-api";
import APIResponseErrorMessage from "../../../commons/errorhandling/api-response-error-message";
import {Col, Row} from "reactstrap";
import { FormGroup, Input, Label} from 'reactstrap';


class UnmapUserEmForm extends React.Component {

    constructor(props) {
        super(props);
        this.toggleForm = this.toggleForm.bind(this);
        this.reloadHandler = this.props.reloadHandler;

        this.state = {

            errorStatus: 0,
            error: null,

            formIsValid: false,

            formControls: {
                emId: {
                    value: '',
                    placeholder: '...',
                    valid: false,
                    touched: false,
                },
                userId: {
                    value: '',
                    placeholder: '...',
                    valid: false,
                    touched: false,
                }
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

    unmapUserEm(pair) {
        return API_EM_USER.unmapUserToEm(pair, (result, status, error) => {
            if (result !== null && (status === 200 || status === 201)) {
                console.log("Successfully inserted person with id: " + result);
                this.reloadHandler();
            } else {
                this.setState(({
                    errorStatus: status,
                    error: error
                }));
            }
        });
    }

    handleSubmit() {
        const pair = {
            emId: this.state.formControls.emId.value,
            userId: this.state.formControls.userId.value
        }
        this.unmapUserEm(pair);
    }

    render() {
        return (
            <div>

                <FormGroup id='emId'>
                    <Label for='emIdField'> Energy Meter ID: </Label>
                    <Input name='emId' id='emIdField' placeholder={this.state.formControls.emId.placeholder}
                           onChange={this.handleChange}
                           defaultValue={this.state.formControls.emId.value}
                           touched={this.state.formControls.emId.touched? 1 : 0}
                           valid={this.state.formControls.emId.valid}
                           required
                    />
                </FormGroup>
                <FormGroup id='userId'>
                    <Label for='userIdField'> User ID: </Label>
                    <Input name='userId' id='userIdField' placeholder={this.state.formControls.userId.placeholder}
                           onChange={this.handleChange}
                           defaultValue={this.state.formControls.userId.value}
                           touched={this.state.formControls.userId.touched? 1 : 0}
                           valid={this.state.formControls.userId.valid}
                           required
                    />
                </FormGroup>

                    <Row>
                        <Col sm={{size: '4', offset: 8}}>
                            <Button type={"submit"} disabled={!this.state.formIsValid} onClick={this.handleSubmit}>  Submit </Button>
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

export default UnmapUserEmForm;
