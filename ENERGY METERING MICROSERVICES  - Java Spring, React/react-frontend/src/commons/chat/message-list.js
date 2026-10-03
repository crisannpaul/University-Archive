import React from 'react';
import MessageItem from './message-item';

class MessageList extends React.Component {
    render() {
        return (
            <div className="message-list">
                {this.props.messages.map((msg, index) => (
                    <MessageItem key={index} message={msg} isOwnMessage={msg.isOwnMessage} />
                ))}
            </div>
        );
    }
}

export default MessageList;
