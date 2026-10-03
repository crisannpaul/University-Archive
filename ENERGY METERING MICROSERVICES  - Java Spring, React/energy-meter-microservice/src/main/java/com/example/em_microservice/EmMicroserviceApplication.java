package com.example.em_microservice;

import com.example.em_microservice.components.MessageProducer;
import com.example.em_microservice.dto.builder.EnergyMeterBuilder;
import com.example.em_microservice.model.Device;
import com.example.em_microservice.repository.DeviceRepository;
import com.example.em_microservice.repository.UserRepository;
import com.example.em_microservice.service.DeviceUserService;
import com.example.em_microservice.service.DeviceService;
import com.example.em_microservice.service.UserService;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.web.client.RestTemplate;

@SpringBootApplication
public class EmMicroserviceApplication {

    public static void main(String[] args) {
        ConfigurableApplicationContext context = SpringApplication.run(EmMicroserviceApplication.class, args);

        DeviceRepository deviceRepository = context.getBean(DeviceRepository.class);
        UserRepository userRepository = context.getBean(UserRepository.class);
        MessageProducer messageProducer = context.getBean(MessageProducer.class);
        RestTemplate restTemplate = context.getBean(RestTemplate.class);

        DeviceService deviceService = new DeviceService(deviceRepository, messageProducer);
        UserService userService = new UserService(userRepository);
        DeviceUserService deviceUserService = new DeviceUserService(deviceRepository, userRepository, messageProducer);

//        User user1 = new User();
//        userService.insert(user1);
//
//        User user2 = new User();
//        userService.insert(user2);

        Device em1 = new Device();
        em1.setName("Contor plita electrica");
        em1.setMaxHourlyRate(500.0);
//        em1.setUser(user1);
        deviceService.insert(EnergyMeterBuilder.toEnergyMeterDTO(em1));

        Device em2 = new Device();
        em2.setName("Voltmetru trifazic");
        em2.setMaxHourlyRate(400.0);
        deviceService.insert(EnergyMeterBuilder.toEnergyMeterDTO(em2));

//        deviceUserService.associateUserWithEnergyMeter(1L, 1L);
    }
}
