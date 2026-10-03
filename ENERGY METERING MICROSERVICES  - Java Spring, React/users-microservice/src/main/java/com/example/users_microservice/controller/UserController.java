package com.example.users_microservice.controller;

import com.example.users_microservice.dto.UserDTO;
import com.example.users_microservice.dto.builder.UserBuilder;
import com.example.users_microservice.model.User;
import com.example.users_microservice.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.List;

@RestController
@CrossOrigin
@RequestMapping(value = "/api/user")
public class UserController {

    private final UserService userService;

    @Autowired
    public UserController(UserService personService) {
        this.userService = personService;
    }

    @GetMapping()
    public ResponseEntity<List<User>> getUsers() {
        List<User> dtos = userService.findUsers();
        return new ResponseEntity<>(dtos, HttpStatus.OK);
    }

    @PostMapping("/addUserLocal")
    public ResponseEntity<Long> insertUser(@RequestBody UserDTO user) {
        Long userID = userService.insert(user);
        return new ResponseEntity<>(userID, HttpStatus.CREATED);
    }

    @PostMapping("/addUserGlobal")
    public ResponseEntity<Long> createUser(@RequestBody UserDTO userDTO) {
        try {
            Long userId = userService.insert(userDTO);
            return new ResponseEntity<>(userId, HttpStatus.CREATED);
        } catch (Exception e) {
            // Log the exception and return an appropriate error response
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    @DeleteMapping("/deleteUser/{userId}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long userId) {
        try {
            userService.delete(userId);
            return new ResponseEntity<>(HttpStatus.NO_CONTENT);
        } catch (Exception e) {
            // Log the exception and return an appropriate error response
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    @PutMapping("/updateUser/{userId}")
    public ResponseEntity<UserDTO> updateUser(@PathVariable Long userId, @RequestBody UserDTO updatedUser) {
        UserDTO updatedUserData = UserBuilder.toUserDTO(userService.update(userId, updatedUser));

        return new ResponseEntity<>(updatedUserData, HttpStatus.OK);
    }

    @GetMapping(value = "/{id}")
    public ResponseEntity<UserDTO> getUser(@PathVariable("id") Long userId) {
        UserDTO dto = userService.findUserById(userId);
        return new ResponseEntity<>(dto, HttpStatus.OK);
    }

}

