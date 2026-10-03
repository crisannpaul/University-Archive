import RestApiClient from "../../commons/api/rest-client";
import {HOST} from "../../commons/api/hosts";


const endpoint = {
    em: '/api/em-user'
};

function getEmUsers(callback) {
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

function mapUserToEm(pair, callback){
    let request = new Request(HOST.em_backend_api + endpoint.em + '/map', {
        method: 'POST',
        headers : {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + localStorage.getItem("jwt")
        },
        body: JSON.stringify(pair)
    });

    console.log("URL: " + request.url);

    RestApiClient.performRequest(request, callback);
}

function unmapUserToEm(pair, callback){
    let request = new Request(HOST.em_backend_api + endpoint.em + '/unmap', {
        method: 'DELETE',
        headers : {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + localStorage.getItem("jwt")
        },
        body: JSON.stringify(pair)
    });

    console.log("URL: " + request.url);

    RestApiClient.performRequest(request, callback);
}

function updateEmUser(emUser, callback){
    let request = new Request(HOST.em_backend_api + endpoint.em + '/' + emUser.id, {
        method: 'PUT',
        headers : {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(emUser)
    });

    console.log("URL: " + request.url);

    RestApiClient.performRequest(request, callback);
}

function deleteEmUser(id, callback){
    let request = new Request(HOST.em_backend_api + endpoint.em + '/' + id, {
        method: 'DELETE',
        headers : {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(id)
    });

    console.log("URL: " + request.url);

    RestApiClient.performRequest(request, callback);
}

export {
    getEmUsers,
    mapUserToEm,
    unmapUserToEm,
    updateEmUser,
    deleteEmUser
};
