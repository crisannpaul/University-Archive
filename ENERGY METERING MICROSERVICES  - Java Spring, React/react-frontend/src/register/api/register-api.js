import {HOST} from "../../commons/api/hosts";
import RestApiClient from "../../commons/api/rest-client";


const endpoint = {
    login: '/api/auth/register'
};

function postRegister(user, callback){
    let request = new Request(HOST.users_backend_api + endpoint.login , {
        method: 'POST',
        headers : {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(user)
    });

    console.log("URL: " + request.url);

    RestApiClient.performRequest(request, callback);
}

export {
    postRegister
};