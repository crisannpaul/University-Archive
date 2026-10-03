import React from 'react';
import ChatHeader from './chat-header';
import MessageList from './message-list';
import ChatInput from './chat-input';
import SockJS from 'sockjs-client';
import Stomp from 'stompjs';
import * as API_USERS from "../../person/api/admin-api";

class UserList extends React.Component {
    render() {
        return (
            <div className="user-list">
                {this.props.users.map(user => (
                    <div key={user.id} onClick={() => this.props.onSelectUser(user)}>
                        {user.username}
                    </div>
                ))}
            </div>
        );
    }
}

export default UserList;



