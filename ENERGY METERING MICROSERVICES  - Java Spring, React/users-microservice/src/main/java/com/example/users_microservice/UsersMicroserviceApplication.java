package com.example.users_microservice;

import com.example.users_microservice.dto.builder.UserBuilder;
import com.example.users_microservice.model.Role;
import com.example.users_microservice.model.User;
import com.example.users_microservice.repository.UserRepository;
import com.example.users_microservice.security.JwtTokenUtil;
import com.example.users_microservice.service.UserService;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.web.client.RestTemplate;

@SpringBootApplication
public class UsersMicroserviceApplication {

    public static void main(String[] args) {
        ConfigurableApplicationContext context = SpringApplication.run(UsersMicroserviceApplication.class, args);

        UserRepository userRepository = context.getBean(UserRepository.class);
        RestTemplate restTemplate = context.getBean(RestTemplate.class);
        JwtTokenUtil jwtTokenUtil = context.getBean(JwtTokenUtil.class);
        UserService userService = new UserService(userRepository, restTemplate, jwtTokenUtil);

        User user1 = new User();
        user1.setUsername("user1");
        user1.setRole(Role.ROLE_CLIENT);
        user1.setEmail("mama@tata.com");
        user1.setPassword("user1");
        userService.insert(UserBuilder.toUserDTO(user1));

        User user2 = new User();
        user2.setUsername("admin");
        user2.setRole(Role.ROLE_ADMIN);
        user2.setEmail("mama@mama.com");
        user2.setPassword("admin");
        userService.insert(UserBuilder.toUserDTO(user2));
    }

}
