import React from 'react';
import './App.css';
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom';
import RegistrationForm from './routes/Registration/Registration.js';
import DonationCenterForm from './routes/RegisterDonationCenteres/RegisterDonation.js';
import DonationCentersMap from './routes/DonationCenterMap/DonationCenterMap.js';
import CallRegistrationSystem from './routes/CallRegistrationSystem/CallRegistrationSystem';
import ProfileConfigForm from './routes/ConfigureUserProfile/ConfigureUserProfile.js';
import ConfigureUserProfileForm from './routes/ConfigureUserProfile/ConfigureUserProfile.js';
import UserProfile from './routes/DisplayUserData/DisplayUserData.js';
import LoginForm from './routes/Login/Login.js';
import Home from './routes/Home/Home.js';
import AdminRequirements from './routes/AdminRequirements/AdminRequirements.js';
import AdminRequirementsForm from './routes/AdminRequirements/AdminRequirements.js';
import AnalysisForm from './routes/AnalysisResults/AnalysisResults.js';
import DonationRequests from './routes/DonationRequests/DonationRequests.js';
import UserDashboard from './routes/DashboardUser/DashboardUser.js';
import AdminDashboard from './routes/AdminDashboard/AdminDashboard.js';
import PostInteractiveContent from './routes/PostInteractiveContent/PostInteractiveContent.js';
import ViewInteractiveContent from './routes/ViewInteractiveContent/ViewInteractiveContent.js';
import DoctorDashboard from './routes/DoctorDashboard/DoctorDashboard.js';
import RecommendInspectionForm from './routes/RecommendInspection/RecommendInspection.js';


import PasswordResetForm from './routes/PasswordReset/PasswordReset.js';
import PasswordReset from './routes/PasswordReset/PasswordReset.js';
import AdminForm from "./routes/Admin/Admin.js";

import RegisterDoctorForm from "./routes/RegisterDoctor/RegisterDoctor.js";
import ManageRequirementsForm from "./routes/DonationRequirements/ManageRequirements.js";
import Layout from "./Layout";
import Logout from "./routes/Logout/Logout";


export default function App() {
    return (
        <div className="App">
            <Router>
                <Routes>
                    <Route path="/" element={<Layout />} >
                        <Route index element={<Home />} />
                        <Route path="/Register" element={<RegistrationForm />} />
                        <Route path="/DonationCenter" element={<DonationCenterForm />} />
                        <Route path="/DonationCenterMap" element={<DonationCentersMap />} />
                        <Route path="/CallRegistrationSystem" element={<CallRegistrationSystem/>} />
                        <Route path="/ConfigureUserProfile" element={<ProfileConfigForm/>} />
                        <Route path="/Login" element={<LoginForm/>} />
                        <Route path="/PasswordReset" element={<PasswordReset/>} />
                        <Route path="/AdminRequirements" element={<AdminRequirements/>} />
                        <Route path="/analysisResults" element={<AnalysisForm/>} />
                        <Route path="/donationRequests" element={<DonationRequests/>} />
                        <Route path="/userDashboard" element={<UserDashboard/>} />
                        <Route path="/adminDashboard" element={<AdminDashboard/>} />
                        <Route path="/post-interactive-content" element={<PostInteractiveContent/>} />
                        <Route path="/viewIneractiveContent" element={<ViewInteractiveContent/>} />
                        <Route path="/doctorDashboard" element={<DoctorDashboard/>} />
                        <Route path="/PasswordReset" element={<PasswordResetForm />} />
                        <Route path="/ConfigureUserProfile" element={<ConfigureUserProfileForm />} />
                        <Route path="/UserProfile" element={<UserProfile />} />
                        <Route path="/AdminRequirements" element={<AdminRequirementsForm />} />
                        <Route path="/Admin" element={<AdminForm />} />
                        <Route path="/RegisterDoctor" element={<RegisterDoctorForm />} />
                        <Route path="/DonationRequirements" element={<ManageRequirementsForm />} />
                        <Route path="/RecommandUsingML" element={<RecommendInspectionForm />} />

                        <Route path="/Logout" element={<Logout />} />
                    </Route>
                </Routes>
            </Router>
        </div>
    );
}
