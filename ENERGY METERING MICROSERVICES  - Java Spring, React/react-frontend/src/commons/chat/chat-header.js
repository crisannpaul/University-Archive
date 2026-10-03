import React from 'react';
import './styles.css'

class ChatHeader extends React.Component {
    render() {
        return (
            <div className="chat-header">
                <h3>Chat with {this.props.chatWith} {this.props.isTyping && " (typing...)"}</h3>
            </div>
        );
    }
}

export default ChatHeader;
