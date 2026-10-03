import React from 'react';
import APIResponseErrorMessage from "../commons/errorhandling/api-response-error-message";
import {
    Button,
    Card,
    CardHeader,
    Col,
    Modal,
    ModalBody,
    ModalHeader,
    Row
} from 'reactstrap';
import {
    DropdownItem,
    DropdownMenu,
    DropdownToggle,
    Nav,
    Navbar,
    NavbarBrand,
    NavLink,
    UncontrolledDropdown
} from 'reactstrap';
import UpdateUsersForm from "./components/users-management/update-user-form";
import { Redirect } from 'react-router-dom';
import * as API_USERS from "./api/admin-api"
import PersonTable from "./components/users-management/users-table";
import AddUsersForm from './components/users-management/add-user-form';
import DeleteUserForm from './components/users-management/delete-user-form';
import UsersManagementContainer from './components/users-management/users-management-container';
import EmManagementContainer from './components/em-management/em-management-container';
import AdminChatWindow from "../commons/chat/admin-chat-window"

const textStyle = {
    color: 'black',
    textDecoration: 'none'
};

const localStorage = window.localStorage;

class AdminPage extends React.Component {

    constructor(props) {
        super(props);
        this.setSelectedEntity = this.setSelectedEntity.bind(this);
        this.reload = this.reload.bind(this);
        this.state = {
            selectedEntity: 'users',
            collapseForm: false,
            tableData: [],
            isLoaded: false,
            errorStatus: 0,
            error: null,
        };
    }



    setSelectedEntity = (entity) => {
        this.setState({selectedEntity: entity});
    }

    reload() {
        this.setState({
            isLoaded: false
        });
    }

    render() {
        let content;
        if(this.state.selectedEntity === 'users') {
            content = <UsersManagementContainer/>
        }
        if(this.state.selectedEntity === 'em') {
            content = <EmManagementContainer/>
        }

        return (
            <div>
                {localStorage.role !== "ROLE_ADMIN" && <Redirect to="/login" push/>}
                <AdminChatWindow/>

                <CardHeader>
                        
                    <UncontrolledDropdown nav inNavbar>
                        <DropdownToggle style={textStyle} nav caret>
                        Table
                        </DropdownToggle>
                        <DropdownMenu right >

                            <DropdownItem onClick={() => this.setSelectedEntity('users')}>
                                Users
                            </DropdownItem>
                            <DropdownItem onClick={() => this.setSelectedEntity('em')}>
                                Energy Meters
                            </DropdownItem>
                            <DropdownItem onClick={() => this.setSelectedEntity('users-em')}>
                                Users-Meters
                            </DropdownItem>


                        </DropdownMenu>
                    </UncontrolledDropdown>

                </CardHeader>
                
                {content}
            </div>
        )

    }
}

export default AdminPage;
