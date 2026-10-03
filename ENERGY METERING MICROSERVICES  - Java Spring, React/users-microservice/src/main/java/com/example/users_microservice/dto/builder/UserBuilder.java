package com.example.users_microservice.dto.builder;

import com.example.users_microservice.dto.UserDTO;
import com.example.users_microservice.model.User;

public class UserBuilder {

    private UserBuilder() {
    }

    public static UserDTO toUserDTO(User user) {
        return new UserDTO(user.getRole(), user.getUsername(), user.getEmail(), user.getPassword());
    }

    public static User toEntity(UserDTO userDTO) {
        User user = new User();
        user.setRole(userDTO.getRole());
        user.setUsername(userDTO.getUsername());
        user.setPassword(userDTO.getPassword());
        user.setEmail(userDTO.getEmail());

        return user;
    }
}

