import React from 'react';
import './styles.css'

class MessageItem extends React.Component {
    render() {
        const { message, isOwnMessage } = this.props;
        const messageClass = isOwnMessage ? "message-own" : "message-other";
        return (
            <div className={`message-item ${messageClass}`}>
                <span>{message.content}</span>
            </div>
        );
    }
}

export default MessageItem;
