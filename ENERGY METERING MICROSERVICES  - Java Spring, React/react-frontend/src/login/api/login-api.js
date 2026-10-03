import RestApiClient from "../../commons/api/rest-client";
import {HOST} from "../../commons/api/hosts";


const endpoint = {
    login: '/api/auth/login'
};

function postLogin(user, callback){
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
    postLogin 
};