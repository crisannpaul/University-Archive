package com.example.users_microservice.service;

import com.example.users_microservice.controller.handlers.exceptions.AlreadyExistsException;
import com.example.users_microservice.controller.handlers.exceptions.InvalidPasswordException;
import com.example.users_microservice.controller.handlers.exceptions.ResourceNotFoundException;
import com.example.users_microservice.dto.UserDTO;
import com.example.users_microservice.dto.builder.UserBuilder;
import com.example.users_microservice.security.JwtTokenUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.example.users_microservice.model.User;
import com.example.users_microservice.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.Optional;

@Service
public class UserService implements UserDetailsService {
    private static final Logger LOGGER = LoggerFactory.getLogger(UserService.class);
    private final UserRepository userRepository;

    private final RestTemplate restTemplate;

    private final JwtTokenUtil jwtTokenUtil;

    @Autowired
    public UserService(UserRepository userRepository, RestTemplate restTemplate, JwtTokenUtil jwtTokenUtil) {
        this.userRepository = userRepository;
        this.restTemplate = restTemplate;
        this.jwtTokenUtil = jwtTokenUtil;
    }

    public User getUserByCredentials(String username, String password) {
        Optional<User> user = userRepository.findUserByUsername(username);

        if(user.isEmpty()) {
            throw new ResourceNotFoundException(User.class.getSimpleName() + " with username: " + username);
        } else {
            if(user.get().getPassword().equals(password)) {
                return user.get();
            } else {
                throw new InvalidPasswordException(User.class.getSimpleName() + " with username: " + username);
            }
        }
    }

    private void checkUserExistence(UserDTO userDTO) {
        Optional<User> existingUser = userRepository.findUserByUsername(userDTO.getUsername());
        if(existingUser.isPresent()) {
            throw new AlreadyExistsException("User with this username exists: " + userDTO.getUsername());
        }

        existingUser = userRepository.findUserByEmail(userDTO.getEmail());
        if(existingUser.isPresent()) {
            throw new AlreadyExistsException("User with this email exists: " + userDTO.getEmail());
        }
    }

    public List<User> findUsers() {
        return userRepository.findAll();
    }

    public UserDTO findUserById(Long id) {
        Optional<User> userOptional = userRepository.findById(id);
        if (userOptional.isEmpty()) {
            LOGGER.error("User with id {} was not found in db", id);
            throw new ResourceNotFoundException(User.class.getSimpleName() + " with id: " + id);
        }
        return UserBuilder.toUserDTO(userOptional.get());
    }

    public Long insert(UserDTO userDTO) {
        checkUserExistence(userDTO);

        String EM_SERVICE_URL = "http://172.30.1.2:8081/springg-demo/api/user/addUser";

        try {
            String adminToken = jwtTokenUtil.generateTokenWithAdminRole(); // Implement this method

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.set("Authorization", "Bearer " + adminToken);
            HttpEntity<UserDTO> entity = new HttpEntity<>(userDTO, headers);

            ResponseEntity<Long> emServiceResponse = restTemplate.postForEntity(
                    EM_SERVICE_URL, entity, Long.class);

            if (emServiceResponse.getStatusCode() == HttpStatus.CREATED) {
                User user = UserBuilder.toEntity(userDTO);
                user = userRepository.save(user);
                LOGGER.debug("User with id {} was inserted in db", user.getUserId());
                return user.getUserId();
            } else {
                throw new RuntimeException("Failed to create user in EM microservice");
            }
        } catch (Exception e) {
            System.out.println(e.toString());
            LOGGER.error("Failed to connect to EM microservice", e);
            User user = UserBuilder.toEntity(userDTO);
            user = userRepository.save(user);
            LOGGER.debug("User with id {} was inserted in db", user.getUserId());
            return user.getUserId();
        }
    }


    public User update(Long userId, UserDTO updatedUser) {
        User existingUser = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + userId));

        existingUser.setRole(updatedUser.getRole());
        existingUser.setUsername(updatedUser.getUsername());
        existingUser.setEmail(updatedUser.getEmail());
        existingUser.setPassword(updatedUser.getPassword());

        return userRepository.save(existingUser);
    }

    public void delete(Long userId) {
        // Step 1: Call the EM microservice to delete the user
        ResponseEntity<Void> emServiceResponse = restTemplate.exchange(
                "http://172.30.1.2:8081/springg-demo/api/user/deleteUser/{userId}",
                HttpMethod.DELETE,
                null,
                Void.class,
                userId
        );

        // Step 2: Check if the user was successfully deleted in the EM microservice
        if (emServiceResponse.getStatusCode() == HttpStatus.NO_CONTENT) {
            // Step 3: Proceed to delete the user in the current microservice
            User existingUser = userRepository.findById(userId)
                    .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + userId));
            userRepository.delete(existingUser);
            LOGGER.debug("User with id {} was deleted from the database", userId);
        } else {
            throw new RuntimeException("Failed to delete user in EM microservice");
        }
    }

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        return userRepository.findUserByUsername(username).orElseThrow(() -> new UsernameNotFoundException("Pula"));
    }
}


