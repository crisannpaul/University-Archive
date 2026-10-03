import React from 'react';

class ChatInput extends React.Component {
    constructor(props) {
        super(props);
        this.state = { message: '' };
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    debounce = (func, delay) => {
        let inDebounce;
        return (...args) => {
            clearTimeout(inDebounce);
            inDebounce = setTimeout(() => {
                func.apply(this, args);
            }, delay);
        };
    };


    handleChange(event) {
        this.setState({ message: event.target.value });
        this.props.onChange();
    }

    handleSubmit(event) {
        event.preventDefault();
        if (this.state.message.trim()) {
            this.props.onSendMessage(this.state.message);
            this.setState({ message: '' });
        }
    }

    render() {
        return (
            <form className="chat-input" onSubmit={this.handleSubmit}>
                <input
                    type="text"
                    value={this.state.message}
                    onChange={this.handleChange}
                    placeholder="Type a message..."
                />
                <button type="submit">Send</button>
            </form>
        );
    }
}

export default ChatInput;
