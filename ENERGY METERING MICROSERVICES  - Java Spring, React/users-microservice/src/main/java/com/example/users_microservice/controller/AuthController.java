package com.example.users_microservice.controller;


import com.example.users_microservice.controller.handlers.exceptions.AlreadyExistsException;
import com.example.users_microservice.controller.handlers.exceptions.InvalidPasswordException;
import com.example.users_microservice.controller.handlers.exceptions.ResourceNotFoundException;
import com.example.users_microservice.dto.UserDTO;
import com.example.users_microservice.model.Role;
import com.example.users_microservice.model.User;
import com.example.users_microservice.security.JwtResponse;
import com.example.users_microservice.security.JwtTokenUtil;
import com.example.users_microservice.service.UserService;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @Autowired
    private UserService userService;

    @Autowired
    private JwtTokenUtil jwtTokenUtil;

    @PostMapping("/login")
    public ResponseEntity<?> authenticateUser(@RequestBody Map<String, String> credentials) {
        String username = credentials.get("username");
        String password = credentials.get("password");

        try {
            User user = userService.getUserByCredentials(username, password);

            // Generate token
            final String token = jwtTokenUtil.generateToken(user);

            return ResponseEntity.ok(new JwtResponse(token));
        } catch (ResourceNotFoundException | InvalidPasswordException e) {
            return new ResponseEntity<>(e.getResource(), e.getStatus());
        }
    }

    @PostMapping("/register")
    public ResponseEntity<String> registerUser(@RequestBody Map<String, String> credentials) {
        String username = credentials.get("username");
        String email = credentials.get("email");
        String password = credentials.get("password");

        UserDTO user = new UserDTO(Role.ROLE_CLIENT, username, email, password);
        ObjectMapper objectMapper = new ObjectMapper();
        try {
            Long userId = userService.insert(user);
            return new ResponseEntity<>(objectMapper.writeValueAsString(user), HttpStatus.OK);
        } catch (AlreadyExistsException e) {
            return new ResponseEntity<>(e.getResource(), e.getStatus());
        } catch (JsonProcessingException e) {
            return new ResponseEntity<>("Nu sa poate", HttpStatus.NO_CONTENT);
        }
    }
}

