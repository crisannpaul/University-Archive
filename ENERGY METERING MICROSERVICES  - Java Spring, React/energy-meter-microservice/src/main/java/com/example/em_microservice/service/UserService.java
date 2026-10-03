package com.example.em_microservice.service;

import com.example.em_microservice.controller.handlers.exceptions.ResourceNotFoundException;
import com.example.em_microservice.model.User;
import com.example.em_microservice.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class UserService {
    private static final Logger LOGGER = LoggerFactory.getLogger(UserService.class);
    private final UserRepository userRepository;

    @Autowired
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public List<User> findUsers() {
        return userRepository.findAll();
    }

    public User findUserById(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> {
                    LOGGER.error("User with id {} was not found in db", id);
                    return new ResourceNotFoundException(User.class.getSimpleName() + " with id: " + id);
                });
    }

    public Long insert(User user) {
        User savedUser = userRepository.save(user);
        LOGGER.debug("User with id {} was inserted in db", savedUser.getUserId());
        return savedUser.getUserId();
    }

    public void delete(Long userId) {
        User existingUser = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + userId));

        userRepository.delete(existingUser);

        LOGGER.debug("User with id {} was deleted from the database", userId);
    }
}

