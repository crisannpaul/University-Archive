import React, {Component} from "react";
import "./Navbar.css";
import {Link} from "react-router-dom";

class Navbar extends Component {
    state = { clicked: false };

    handleClick = () => {
        this.setState({ clicked: !this.state.clicked });
    };

    userRole = sessionStorage.getItem('role');

    render() {
        return (
            <nav className="NavbarItems">
                <h1 className="navbar-logo"></h1>
                <div className="menu-icons" onClick={this.handleClick}></div>
                <ul className={this.state.clicked ? "nav-menu active" : "nav-menu"}>
                    {MenuItems.map((item, index) => {
                        if (item.title === "Logout" && this.userRole == null)
                            // eslint-disable-next-line array-callback-return
                            return;

                        if (item.title === "Login" && this.userRole != null)
                            // eslint-disable-next-line array-callback-return
                            return;

                        return (
                            <li key={index}>
                                <Link className={item.cName} to={item.url}>
                                    {item.title}
                                </Link>
                            </li>

                        );
                    })}
                </ul>
            </nav>
        );
    }
}

export default Navbar;

export const MenuItems = [
    {
        url: "/",
        cName: "nav-links",
        title: "Home",
    },

    {
        url: "/register",
        cName: "nav-links",
        title: "Regsiter",
    },
    {
        url: "/DonationCenter",
        cName: "nav-links",
        title: "Donation Centers",
    },

    {
        url: "/AdminRequirements",
        cName: "nav-links",
        title: "Donation Requirements",
    },

    {
        url: "/CallRegistrationSystem",
        cName: "nav-links",
        title: "Register Calls",
    },

    {
        url: "/UserProfile",
        cName: "nav-links",
        title: "User Data",
    },

    {
        url: "/ConfigureUserProfile",
        cName: "nav-links",
        title: "Configure User Profile",
    },

    {
        url: "/PasswordReset",
        cName: "nav-links",
        title: "Password Reset",
    },

    {
        url: "/logout",
        cName: "nav-links",
        title: "Logout",
    },

    {
        url: "/login",
        cName: "nav-links",
        title: "Login",
    },
    
];
