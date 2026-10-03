package com.example.communication_microservice;

import com.example.communication_microservice.repository.EnergyDataRepository;
import com.example.communication_microservice.service.DeviceService;
import com.example.communication_microservice.service.EnergyDataService;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.scheduling.annotation.EnableScheduling;

import java.util.Date;

@EnableScheduling
@SpringBootApplication
public class CommunicationMicroserviceApplication {

    public static void main(String[] args) {
        ConfigurableApplicationContext context = SpringApplication.run(CommunicationMicroserviceApplication.class, args);


        EnergyDataRepository energyDataRepository = context.getBean(EnergyDataRepository.class);
        DeviceService deviceService = context.getBean(DeviceService.class);
        EnergyDataService energyDataService = new EnergyDataService(energyDataRepository, deviceService);

//        energyDataService.createMessage(new Date(), 1L, 1.5);
    }

}
