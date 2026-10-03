import {useNavigate} from 'react-router-dom';
import {useEffect} from "react";
import { Store } from 'react-notifications-component';

function Logout() {
    const navigate = useNavigate();

    useEffect(() => {

        sessionStorage.removeItem('token');
        sessionStorage.removeItem('id');
        sessionStorage.removeItem('role');

        console.log('Logout successfully');
        Store.addNotification({
            title: "Wonderful!",
            message: "Logout successfully",
            type: "success",
            insert: "top",
            container: "top-right",
            dismiss: {
                duration: 1000,
                onScreen: true
            },
        });

        navigate("/login");
    }, []);
}

export default Logout;
