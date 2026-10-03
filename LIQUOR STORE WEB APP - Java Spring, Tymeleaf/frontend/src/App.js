import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Home from "./routes/Home";
import About from "./routes/About";
import Menu from "./routes/Menu";
import Contact from "./routes/Contact";
import Register from "./routes/Register";
import Login from "./routes/Login";
import Log from "./routes/Log";
import './App.css';
import { Routes, Route } from 'react-router-dom';


export default function App() {
    
    return (
        <div className="App">
           
            <Routes>
                <Route path="/" element={<Home/>}/>
                <Route path="/about" element={<About/>}/>
                <Route path="/menu" element={<Menu/>}/>
                <Route path="/contact" element={<Contact/>}/>
                <Route path="/signup" element={<Login/>}/>
                <Route path="/register" element={<Register/>}>
                </Route>
            </Routes>
            

            
            
                
            
        </div>
    );
}

