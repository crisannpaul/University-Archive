import {Outlet} from "react-router-dom";
import Navbar from "./routes/Navbar/Navbar";
import {ReactNotifications, Store} from 'react-notifications-component'
import 'react-notifications-component/dist/theme.css'
import {useEffect, useState} from "react";

const Layout = () => {
    const [messages, setMessages] = useState([]);
    let userId = sessionStorage.getItem('id');

    useEffect(() => {
        if (userId == null)
            return;

        const socket = new WebSocket(`ws://localhost:8080/ws?id=${userId}`);

        socket.onopen = () => {
            console.log('WebSocket connection opened');
        };

        socket.onmessage = (event) => {
            console.log('Message received from server:', event.data);
            setMessages((prevMessages) => [...prevMessages, event.data]);
        };

        socket.onclose = (event) => {
            if (event.wasClean) {
                console.log('WebSocket connection closed cleanly');
            } else {
                console.log('WebSocket connection closed abruptly');
            }
            console.log('Code:', event.code, 'Reason:', event.reason);
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        return () => {
            socket.close();
        };
    }, [userId]);

    useEffect(() => {
        if (userId == null)
            return;

        messages.map((notification, index) => (
            Store.addNotification({
                title: "INFO",
                message: notification,
                type: "info",
                insert: "top",
                container: "top-right",
                dismiss: {
                    duration: 1000,
                    onScreen: true
                },
            })
        ))

    }, [messages]);

    return (
        <>
            <ReactNotifications   />
            <Navbar/>
            <Outlet />
        </>
    )
};

export default Layout;