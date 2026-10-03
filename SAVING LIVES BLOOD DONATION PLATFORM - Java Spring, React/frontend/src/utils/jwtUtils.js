import {jwtDecode} from 'jwt-decode'

export const getUserIdFromJWT = (token) => {
    if (!token) {
        console.log('No token found in local storage.');
        return null;
    }
    try {
        const decoded = jwtDecode(token);
        return decoded.id;
    } catch (error) {
        console.error('Failed to decode JWT:', error);
        return null;
    }
};
