import RestApiClient from "../../commons/api/rest-client";
import {HOST} from "../../commons/api/hosts";


const endpoint = {
    em: '/api/energy-meter'
};

function getEnergyMeters(callback) {
    let request = new Request(HOST.em_backend_api + endpoint.em, {
        method: 'GET',
        headers : {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + localStorage.getItem("jwt")
        }
    });
    console.log(request.url);
    RestApiClient.performRequest(request, callback);
}

function getEnergyMetersByUserId(userId, callback) {
    let request = new Request(HOST.em_backend_api + endpoint.em + '/user/' + userId, {
        method: 'GET',
        headers : {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + localStorage.getItem("jwt")
        }
    });
    console.log(request.url);
    RestApiClient.performRequest(request, callback);
}

export {
    getEnergyMeters,
    getEnergyMetersByUserId
};
