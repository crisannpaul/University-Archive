import RestApiClient from "../../commons/api/rest-client";
import {HOST} from "../../commons/api/hosts";


const endpoint = {
    em: '/api/energy-consumption'
};

function getEnergyDataByUserIdAndDate(userId, date, callback) {
    let request = new Request(HOST.energy_data_api + endpoint.em + '/' + userId + '/' + date, {
        method: 'GET',
    });
    console.log(request.url);
    RestApiClient.performRequest(request, callback);
}

export {
    getEnergyDataByUserIdAndDate // Export the new method
};