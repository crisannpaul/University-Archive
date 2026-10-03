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
import UpdateEmForm from "./update-em-form";
import * as API_EM from '../../api/em-api'
import AddEmForm from './add-em-form';
import DeleteEmForm from './delete-em-form';
import EnergyMeterTable from './em-table';
import MapUserEmForm from './map-user-em-form';
import UnmapUserEmForm from './unmap-user-em-form';

const textStyle = {
    color: 'black',
    textDecoration: 'none'
};

class EmManagementContainer extends React.Component {

    constructor(props) {
        super(props);
        this.toggleAddForm = this.toggleAddForm.bind(this);
        this.toggleUpdateForm = this.toggleUpdateForm.bind(this);
        this.toggleDeleteForm = this.toggleDeleteForm.bind(this);
        this.toggleMapUserForm = this.toggleMapUserForm.bind(this);
        this.toggleUnmapUserForm = this.toggleUnmapUserForm.bind(this);
        this.reload = this.reload.bind(this);
        this.state = {
            addFormSelected: false,
            updateFormSelected: false,
            deleteFormSelected: false,
            mapUserFormSelected: false,
            unmapUserFormSelected: false,
            collapseForm: false,
            tableData: [],
            isLoaded: false,
            errorStatus: 0,
            error: null
        };
    }

    componentDidMount() {
        this.fetchEnergyMeters();
    }

    fetchEnergyMeters() {
        return API_EM.getEnergyMeters((result, status, err) => {

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

    toggleMapUserForm() {
        this.setState({mapUserFormSelected: !this.state.mapUserFormSelected});
    }

    toggleUnmapUserForm() {
        this.setState({unmapUserFormSelected: !this.state.unmapUserFormSelected});
    }


    reload() {
        this.setState({
            isLoaded: false
        });
        this.toggleAddForm();
        this.toggleUpdateForm();
        this.toggleDeleteForm();
        this.toggleMapUserForm();
        this.toggleUnmapUserForm();
        this.fetchEnergyMeters();
    }

    render() {
        return (
            <div>
                <Card>
                    <Row>
                        <Col sm={{size: '8', offset: 1}}>
                            {this.state.isLoaded && <EnergyMeterTable  tableData = {this.state.tableData}/>}
                            {this.state.errorStatus > 0 && <APIResponseErrorMessage
                                                            errorStatus={this.state.errorStatus}
                                                            error={this.state.error}
                                                        />   }
                        </Col>
                    </Row>
                    <br/>
                    <Row>
                        <Col sm={{size: '8', offset: 1}}>
                            <Button color="primary" onClick={this.toggleAddForm}>Add Energy Meter </Button>
                            <Button color="primary" onClick={this.toggleUpdateForm}>Edit Energy Meter </Button>
                            <Button color="primary" onClick={this.toggleDeleteForm}>Delete Energy Meter </Button>
                            <Button color="primary" onClick={this.toggleMapUserForm}>Map User To Energy Meter </Button>
                            <Button color="primary" onClick={this.toggleUnmapUserForm}>Unmap User From Energy Meter</Button>

                        </Col>
                    </Row>
                    <br/>
                </Card>
                
                <Modal isOpen={this.state.addFormSelected} toggle={this.toggleAddForm}
                       className={this.props.className} size="lg">
                    <ModalHeader toggle={this.toggleAddForm}> Add Energy Meter: </ModalHeader>
                    <ModalBody>
                        <AddEmForm reloadHandler={this.reload}/>
                    </ModalBody>
                </Modal>

                <Modal isOpen={this.state.updateFormSelected} toggle={this.toggleUpdateForm}
                       className={this.props.className} size="lg">
                    <ModalHeader toggle={this.toggleUpdateForm}> Edit Energy Meter: </ModalHeader>
                    <ModalBody>
                        <UpdateEmForm reloadHandler={this.reload}/>
                    </ModalBody>
                </Modal>

                <Modal isOpen={this.state.deleteFormSelected} toggle={this.toggleDeleteForm}
                       className={this.props.className} size="lg">
                    <ModalHeader toggle={this.toggleDeleteForm}> Delete Energy Meter: </ModalHeader>
                    <ModalBody>
                        <DeleteEmForm reloadHandler={this.reload}/>
                    </ModalBody>
                </Modal>

                <Modal isOpen={this.state.mapUserFormSelected} toggle={this.toggleMapUserForm}
                       className={this.props.className} size="lg">
                    <ModalHeader toggle={this.toggleMapUserForm}> Map Energy Meter To User: </ModalHeader>
                    <ModalBody>
                        <MapUserEmForm reloadHandler={this.reload}/>
                    </ModalBody>
                </Modal>

                <Modal isOpen={this.state.unmapUserFormSelected} toggle={this.toggleUnmapUserForm}
                       className={this.props.className} size="lg">
                    <ModalHeader toggle={this.toggleUnmapUserForm}> Unamp Energy Meter From User: </ModalHeader>
                    <ModalBody>
                        <UnmapUserEmForm reloadHandler={this.reload}/>
                    </ModalBody>
                </Modal>

            </div>
        )

    }
}

export default EmManagementContainer;
