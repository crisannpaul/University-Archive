import React from 'react';
import ChatHeader from './chat-header';
import MessageList from './message-list';
import ChatInput from './chat-input';
import SockJS from 'sockjs-client';
import Stomp from 'stompjs';
import './styles.css'
import {getChatHistory} from "./chat-api";
import messageItem from "./message-item";
import {HOST} from "../api/hosts"


class UserChatWindow extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            stompClient: null,
            messages: [],
            sender: props.sender,
            receiver: 'admin',
            otherUserIsTyping: false
        };
    }

    componentDidMount() {
        const socket = new SockJS(HOST.chat_api + '/chat-socket');
        const client = Stomp.over(socket);

        client.connect({}, () => {
            this.setState({ stompClient: client });

            // Subscribe to receive messages
            client.subscribe(`/topic/users/${this.state.sender}`, (message) => {
                console.log(message)
                const newMessage = JSON.parse(message.body);
                this.handleIncomingMessage(newMessage)
            });
        });

        getChatHistory(this.state.sender, this.state.receiver, (result, status, err) => {
            if (result !== null && status === 200) {
                console.log(result);

                const formattedMessages = result.map(message => ({
                    ...message,
                    isOwnMessage: message.sender === this.state.sender
                }));

                this.setState({ messages: formattedMessages });
            } else {
                // Handle errors or no response
            }
        });
    }

    componentWillUnmount() {
        // Disconnect the WebSocket
        if (this.state.stompClient) {
            this.state.stompClient.disconnect();
        }
    }

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
        const { stompClient, sender } = this.state;
        if (stompClient && stompClient.connected) {
            const chatMessage = {
                type: "CHAT",
                content: messageContent,
                sender: sender,
                receiver: this.state.receiver,
            };
            this.handleIncomingMessage(chatMessage)
            stompClient.send("/app/send-message", {}, JSON.stringify(chatMessage));
        }
    };

    sendTyping = () => {
        const { stompClient, sender } = this.state;

        if (stompClient && stompClient.connected) {
            const typingMessage = {
                type: "TYPING",
                content: '',
                sender: sender,
                receiver: this.state.receiver,
            };
            stompClient.send("/app/send-message", {}, JSON.stringify(typingMessage));
        }
    };


    render() {
        const { messages } = this.state;

        return (
            <div className="chat-window">
                <ChatHeader chatWith={this.state.receiver} isTyping={this.state.otherUserIsTyping}/>/>
                <MessageList messages={messages} />
                <ChatInput onSendMessage={this.sendMessage} onChange={this.sendTyping}/>
            </div>
        );
    }
}

export default UserChatWindow;

