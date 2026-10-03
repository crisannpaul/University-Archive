import {HOST} from "../../commons/api/hosts";
import RestApiClient from "../../commons/api/rest-client";


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

function insertEnergyMeter(energyMeter, callback){
    let request = new Request(HOST.em_backend_api + endpoint.em, {
        method: 'POST',
        headers : {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + localStorage.getItem("jwt")
        },
        body: JSON.stringify(energyMeter)
    });

    console.log("URL: " + request.url);

    RestApiClient.performRequest(request, callback);
}

function updateEnergyMeter(energyMeter, callback){
    let request = new Request(HOST.em_backend_api + endpoint.em + '/' + energyMeter.id, {
        method: 'PUT',
        headers : {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + localStorage.getItem("jwt")
        },
        body: JSON.stringify(energyMeter)
    });

    console.log("URL: " + request.url);

    RestApiClient.performRequest(request, callback);
}

function deleteEnergyMeter(id, callback){
    let request = new Request(HOST.em_backend_api + endpoint.em + '/' + id, {
        method: 'DELETE',
        headers : {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + localStorage.getItem("jwt")
        },
        body: JSON.stringify(id)
    });

    console.log("URL: " + request.url);

    RestApiClient.performRequest(request, callback);
}

export {
    getEnergyMeters,
    insertEnergyMeter,
    updateEnergyMeter,
    deleteEnergyMeter
};
