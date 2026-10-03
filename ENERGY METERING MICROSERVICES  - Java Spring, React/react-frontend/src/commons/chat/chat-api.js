import RestApiClient from "../../commons/api/rest-client";
import {HOST} from "../api/hosts";

const endpoint = {
     chat: '/api/messages'
};

function getChatHistory(sender, receiver, callback) {
    const urlWithParams = HOST.chat_api + endpoint.chat + '/history' + `?user1=${encodeURIComponent(sender)}&user2=${encodeURIComponent(receiver)}`;

    let request = new Request(urlWithParams, {
        method: 'GET',
        headers : {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
    });

    RestApiClient.performRequest(request, callback);
}

export {
    getChatHistory
}

