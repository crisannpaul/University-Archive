import RestApiClient from "../../commons/api/rest-client";
import {HOST} from "../../commons/api/hosts";


const endpoint = {
    user: '/api/user'
};

function getUsers(callback) {
    console.log(localStorage.getItem("jwt"))
    let request = new Request(HOST.users_backend_api + endpoint.user, {
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

function getUserById(id, callback){
    let request = new Request(HOST.users_backend_api + endpoint.user + '/'+ id, {
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

function updateUser(user, callback){
    const updateUrl = '/updateUser' + '/' + user.id 
    let request = new Request(HOST.users_backend_api + endpoint.user + updateUrl, {
        method: 'PUT',
        headers : {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + localStorage.getItem("jwt")
        },
        body: JSON.stringify(user)
    });

    console.log("URL: " + request.url);

    RestApiClient.performRequest(request, callback);
}

function insertUser(user, callback){
    const insertUrl = '/addUserGlobal'
    let request = new Request(HOST.users_backend_api + endpoint.user + insertUrl, {
        method: 'POST',
        headers : {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + localStorage.getItem("jwt")
        },
        body: JSON.stringify(user)
    });

    console.log("URL: " + request.url);

    RestApiClient.performRequest(request, callback);
}

function deleteUser(id, callback){
    const deleteUrl = '/deleteUser/' + id
    let request = new Request(HOST.users_backend_api + endpoint.user + deleteUrl, {
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
    getUsers,
    updateUser,
    getUserById,
    insertUser,
    deleteUser
};
