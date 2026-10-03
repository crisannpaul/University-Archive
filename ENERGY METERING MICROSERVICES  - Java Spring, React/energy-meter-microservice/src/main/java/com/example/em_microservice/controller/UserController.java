package com.example.em_microservice.controller;

import com.example.em_microservice.model.User;
import com.example.em_microservice.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@CrossOrigin
@RequestMapping(value = "/api/user")
public class UserController {

    private final UserService userService;

    @Autowired
    public UserController(UserService userService) {
        this.userService = userService;
    }


    @PostMapping(value = "/addUser")
    public ResponseEntity<Long> addNewUser(@RequestBody User user) {
        // Call the service method to add the new user
        Long userId = userService.insert(user);

        if (userId != null) {
            // User added successfully, return HTTP 201 with the ID
            return new ResponseEntity<>(userId, HttpStatus.CREATED);
        } else {
            // Handle the case where adding the user failed
            // Return an error response or handle it as needed.
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    @DeleteMapping("/deleteUser/{userId}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long userId) {
        userService.delete(userId);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }
}

