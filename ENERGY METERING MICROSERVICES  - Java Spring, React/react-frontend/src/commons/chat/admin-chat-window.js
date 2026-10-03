import React from 'react';
import ChatHeader from './chat-header';
import MessageList from './message-list';
import ChatInput from './chat-input';
import SockJS from 'sockjs-client';
import Stomp from 'stompjs';
import UserChatWindow from "./user-chat-window";
import UserList from "./user-list";
import * as API_USERS from "../../person/api/admin-api";
import {getChatHistory} from "./chat-api";
import './styles.css'
import {HOST} from "../api/hosts";

class AdminChatWindow extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            stompClient: null,
            messages: [],
            selectedUser: null,
            users: null,
            isLoaded: false,
            sender: "admin",
            otherUserIsTyping: false
        };
    }

    componentDidMount() {
        this.fetchPersons()

        const socket = new SockJS(HOST.chat_api + '/chat-socket');
        const client = Stomp.over(socket);

        client.connect({}, () => {
            this.setState({ stompClient: client });

            if (client) {
                client.subscribe(`/topic/admin`, (message) => {
                    console.log(message)
                    const newMessage = JSON.parse(message.body);
                    this.handleIncomingMessage(newMessage);
                });
            }
        });
    }

    componentWillUnmount() {
        // Disconnect the WebSocket
        if (this.state.stompClient) {
            this.state.stompClient.disconnect();
        }
    }

    onSelectUser = (user) => {
        this.setState({ selectedUser: user });

        const adminUsername = this.state.sender;

        getChatHistory(adminUsername, user.username, (result, status, err) => {
            if (result !== null && status === 200) {
                console.log(result);

                const formattedMessages = result.map(message => ({
                    ...message,
                    isOwnMessage: message.sender === adminUsername
                }));

                this.setState({ messages: formattedMessages });
            } else {
                // Handle errors or no response
            }
        });
    };


    handleIncomingMessage = (newMessage) => {
        if (newMessage.type === "TYPING") {
            // Handle typing notification
            // For example, set a state to show the typing indicator in the UI
            this.setState({ otherUserIsTyping: true });

            // Optionally, use a timeout to hide the typing indicator after a short period
            clearTimeout(this.typingTimeout);
            this.typingTimeout = setTimeout(() => {
                this.setState({ otherUserIsTyping: false });
            }, 3000); // Hide typing indicator after 3 seconds of inactivity

        } else {
            // Handle regular chat messages
            const isOwnMessage = newMessage.sender === this.state.sender;

            const formattedMessage = {
                ...newMessage,
                isOwnMessage: isOwnMessage
            };

            this.setState(prevState => ({
                messages: [...prevState.messages, formattedMessage]
            }));
        }
        console.log(this.state.messages);
    };


    sendMessage = (messageContent) => {
        const { stompClient, selectedUser } = this.state;
        if (stompClient && stompClient.connected) {
            const chatMessage = {
                type: "CHAT",
                content: messageContent,
                sender: this.state.sender,
                receiver: selectedUser.username,
            };
            this.handleIncomingMessage(chatMessage)
            stompClient.send("/app/send-message", {}, JSON.stringify(chatMessage));
        }
    };

    sendTyping = () => {
        const { stompClient, selectedUser } = this.state;

        if (stompClient && stompClient.connected){
            const typingMessage = {
                type: "TYPING",
                content: '',
                sender: this.state.sender,
                receiver: selectedUser.username,
            };
            stompClient.send("/app/send-message", {}, JSON.stringify(typingMessage));
        }
    };

    fetchPersons() {
        return API_USERS.getUsers((result, status, err) => {
            if (result !== null && status === 200) {
                console.log(result);

                const users = result.map(user => ({
                    id: user.id,
                    username: user.username
                }));

                this.setState({
                    users: users,
                    isLoaded: true
                });
            } else {
                this.setState({
                    errorStatus: status,
                    error: err
                });
            }
        });
    }

    render() {
        const { selectedUser, messages } = this.state;

        return (
            <div>
                {this.state.isLoaded && <UserList users={this.state.users} onSelectUser={this.onSelectUser}/>}
                {selectedUser && (
                    <div className="chat-window">
                        <ChatHeader chatWith={selectedUser.username} isTyping={this.state.otherUserIsTyping}/>
                        <MessageList messages={messages} />
                        <ChatInput onSendMessage={this.sendMessage} onChange={this.sendTyping}/>
                    </div>
                )}
            </div>
        );
    }
}

export default AdminChatWindow;
