import React, {useState} from 'react';
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

import * as API_EM from "./api/em-api"
import * as API_DATA from "./api/consumption-api"
import EnergyMeterTable from './components/em-table';
import { Redirect } from 'react-router-dom';
import SockJS from 'sockjs-client';
import Stomp from 'stompjs';
import {CartesianGrid, Legend, Line, LineChart, Tooltip, XAxis, YAxis} from "recharts";
import DatePicker from "react-datepicker";
import UserChatWindow from "../commons/chat/user-chat-window";
import {HOST} from "../commons/api/hosts"


const localStorage = window.localStorage;

class UserPage extends React.Component {

    constructor(props) {
        super(props);
        this.reload = this.reload.bind(this);
        this.state = {
            addFormSelected: false,
            updateFormSelected: false,
            deleteFormSelected: false,
            collapseForm: false,
            tableData: [],
            isLoaded: false,
            errorStatus: 0,
            error: null,
            notification: '',
            showModal: false,
            selectedDate: new Date(),
            energyData: [],
        };
        this.stompClient = null;
    }

    componentDidMount() {
        this.fetchPersons();
        this.connectWebSocket();
    }

    componentWillUnmount() {
        if (this.stompClient) {
            this.stompClient.disconnect();
        }
    }

    // handleDateChange = (date) => {
    //     this.setState({
    //         selectedDate: date
    //     }, () => {
    //         this.fetchEnergyData();
    //     });
    // };

    connectWebSocket() {
        const url = 'http://172.30.2.2:8082'

        const socket = new SockJS(HOST.energy_data_api + '/ws');
        this.stompClient = Stomp.over(socket);
        const currentUserId = localStorage.getItem('id');

        this.stompClient.connect({}, frame => {
            this.stompClient.subscribe('/topic/user.' + currentUserId, notification => {
                this.setState({
                    notification: notification.body,
                    showModal: true
                });

            });
        });
    }

    fetchPersons() {
        const userId = localStorage.id;

        return API_EM.getEnergyMetersByUserId(userId, (result, status, err) => {
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

    // fetchEnergyData = () => {
    //     const { selectedDate } = this.state;
    //     const userId = localStorage.getItem('id');
    //     const formattedDate = selectedDate.toISOString().split('T')[0]; // Format date as YYYY-MM-DD
    //
    //     API_DATA.getEnergyDataByUserIdAndDate(userId, formattedDate, (result, status, err) => {
    //         // Assume the API returns an array of objects with 'hour' and 'value' keys
    //         if (result !== null && status === 200) {
    //             const dataForChart = Object.entries(result).map(([hour, value]) => {
    //                 return { hour, value };
    //             });
    //             console.log(dataForChart)
    //             this.setState({
    //                 energyData: dataForChart
    //             });
    //         } else {
    //             // Handle errors
    //         }
    //     });
    // };

    reload() {
        this.setState({
            isLoaded: false
        });
        this.fetchPersons();
    }

    toggleModal = () => {
        this.setState({ showModal: !this.state.showModal });
    }
    render() {
        return (
            <div>
                <div>
                    {localStorage.role !== "ROLE_CLIENT" && <Redirect to="/login" push/>}

                    <Modal isOpen={this.state.showModal} toggle={this.toggleModal}>
                        <ModalHeader toggle={this.toggleModal}>Notification</ModalHeader>
                        <ModalBody>
                            {this.state.notification}
                        </ModalBody>
                    </Modal>

                    <CardHeader>
                        <strong> Energy Meters </strong>
                    </CardHeader>
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
                    </Card>
                </div>
                <UserChatWindow sender={localStorage.username}/>

                {/*<div>*/}
                {/*    <DatePicker*/}
                {/*        selected={this.state.selectedDate}*/}
                {/*        onChange={this.handleDateChange}*/}
                {/*    />*/}
                {/*    {}*/}
                {/*    <LineChart width={700} height={300} data={this.state.energyData}>*/}
                {/*        <CartesianGrid stroke="#ccc" />*/}
                {/*        <XAxis dataKey="hour" />*/}
                {/*        <YAxis/>*/}
                {/*        /!*<Tooltip />*!/*/}
                {/*        <Line type="monotone" dataKey="value" stroke="#8884d8" />*/}
                {/*    </LineChart>*/}
                {/*</div>*/}
            </div>
        )

    }
}

export default UserPage;
