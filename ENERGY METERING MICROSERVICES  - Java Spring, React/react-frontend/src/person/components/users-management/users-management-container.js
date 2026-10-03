import React from 'react';
import APIResponseErrorMessage from '../../../commons/errorhandling/api-response-error-message';
import {
    Button,
    Card,
    Col,
    Modal,
    ModalBody,
    ModalHeader,
    Row
} from 'reactstrap';
import UpdateUsersForm from "./update-user-form";
import * as API_USERS from '../../api/admin-api'
import PersonTable from "./users-table";
import AddUsersForm from './add-user-form';
import DeleteUserForm from './delete-user-form';

const textStyle = {
    color: 'black',
    textDecoration: 'none'
};

class UsersManagementContainer extends React.Component {

    constructor(props) {
        super(props);
        this.toggleAddForm = this.toggleAddForm.bind(this);
        this.toggleUpdateForm = this.toggleUpdateForm.bind(this);
        this.toggleDeleteForm = this.toggleDeleteForm.bind(this);
        this.reload = this.reload.bind(this);
        this.state = {
            addFormSelected: false,
            updateFormSelected: false,
            deleteFormSelected: false,
            collapseForm: false,
            tableData: [],
            isLoaded: false,
            errorStatus: 0,
            error: null
        };
    }

    componentDidMount() {
        this.fetchPersons();
    }

    fetchPersons() {
        return API_USERS.getUsers((result, status, err) => {

            if (result !== null && status === 200) {
                console.log(result)
                this.setState({
                    tableData: result,
                    isLoaded: true
                });
            } else {
                this.setState(({
                    errorStatus: status,
                    error: err
                }));
            }
        });
    }

    toggleAddForm() {
        this.setState({addFormSelected: !this.state.addFormSelected});
    }

    toggleUpdateForm() {
        this.setState({updateFormSelected: !this.state.updateFormSelected});
    }

    toggleDeleteForm() {
        this.setState({deleteFormSelected: !this.state.deleteFormSelected});
    }


    reload() {
        this.setState({
            isLoaded: false
        });
        this.toggleAddForm();
        this.toggleUpdateForm();
        this.toggleDeleteForm();
        this.fetchPersons();
    }

    render() {
        return (
            <div>
                <Card>
                    <Row>
                        <Col sm={{size: '8', offset: 1}}>
                            {this.state.isLoaded && <PersonTable  tableData = {this.state.tableData}/>}
                            {this.state.errorStatus > 0 && <APIResponseErrorMessage
                                                            errorStatus={this.state.errorStatus}
                                                            error={this.state.error}
                                                        />   }
                        </Col>
                    </Row>
                    <br/>
                    <Row>
                        <Col sm={{size: '8', offset: 1}}>
                            <Button color="primary" onClick={this.toggleAddForm}>Add User </Button>
                            <Button color="primary" onClick={this.toggleUpdateForm}>Edit User </Button>
                            <Button color="primary" onClick={this.toggleDeleteForm}>Delete User </Button>
                        </Col>
                    </Row>
                    <br/>
                </Card>
                
                <Modal isOpen={this.state.addFormSelected} toggle={this.toggleAddForm}
                       className={this.props.className} size="lg">
                    <ModalHeader toggle={this.toggleAddForm}> Add user: </ModalHeader>
                    <ModalBody>
                        <AddUsersForm reloadHandler={this.reload}/>
                    </ModalBody>
                </Modal>

                <Modal isOpen={this.state.updateFormSelected} toggle={this.toggleUpdateForm}
                       className={this.props.className} size="lg">
                    <ModalHeader toggle={this.toggleUpdateForm}> Edit user: </ModalHeader>
                    <ModalBody>
                        <UpdateUsersForm reloadHandler={this.reload}/>
                    </ModalBody>
                </Modal>

                <Modal isOpen={this.state.deleteFormSelected} toggle={this.toggleDeleteForm}
                       className={this.props.className} size="lg">
                    <ModalHeader toggle={this.toggleDeleteForm}> Delete user: </ModalHeader>
                    <ModalBody>
                        <DeleteUserForm reloadHandler={this.reload}/>
                    </ModalBody>
                </Modal>

            </div>
        )

    }
}

export default UsersManagementContainer;
