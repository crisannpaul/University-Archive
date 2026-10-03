package com.example.em_microservice.service;

import com.example.em_microservice.components.MessageProducer;
import com.example.em_microservice.controller.handlers.exceptions.ResourceNotFoundException;
import com.example.em_microservice.dto.DeviceUserDTO;
import com.example.em_microservice.model.Device;
import com.example.em_microservice.model.User;
import com.example.em_microservice.repository.DeviceRepository;
import com.example.em_microservice.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;

@Service
public class DeviceUserService {

    private static final Logger LOGGER = LoggerFactory.getLogger(DeviceUserService.class);
    private final DeviceRepository deviceRepository;
    private final UserRepository userRepository;

    private final MessageProducer messageProducer;

    @Autowired
    public DeviceUserService(DeviceRepository deviceRepository, UserRepository userRepository, MessageProducer messageProducer) {
        this.deviceRepository = deviceRepository;
        this.userRepository = userRepository;
        this.messageProducer = messageProducer;
    }

    public List<DeviceUserDTO> getAllEnergyMeterUserMappings() {
        List<Device> devices = deviceRepository.findAll();

        List<DeviceUserDTO> mappings = new ArrayList<>();

        for (Device device : devices) {
            User user = device.getUser();
            DeviceUserDTO mapping = new DeviceUserDTO(device.getEnergyMeterId(), user.getUserId());
            mappings.add(mapping);
        }

        return mappings;
    }

    @Transactional
    public void associateUserWithEnergyMeter(Long energyMeterId, Long userId) {
        Device device = deviceRepository.findById(energyMeterId)
                .orElseThrow(() -> {
                    LOGGER.error("EnergyMeter with id {} was not found in db", energyMeterId);
                    return new ResourceNotFoundException(Device.class.getSimpleName() + " with id: " + energyMeterId);
                });

        User user = userRepository.findById(userId)
                .orElseThrow(() -> {
                    LOGGER.error("User with id {} was not found in db", userId);
                    return new ResourceNotFoundException(User.class.getSimpleName() + " with id: " + userId);
                });

        device.setUser(user);
        messageProducer.sendDeviceMessage(device,"UPDATE");
        deviceRepository.save(device);
    }

    @Transactional
    public void updateAssociation(Long energyMeterId, Long newUserId) {
        Device device = deviceRepository.findById(energyMeterId)
                .orElseThrow(() -> {
                    String errorMessage = "EnergyMeter with id " + energyMeterId + " was not found in the database.";
                    LOGGER.error(errorMessage);
                    return new ResourceNotFoundException(errorMessage);
                });

        User newUser = userRepository.findById(newUserId)
                .orElseThrow(() -> {
                    String errorMessage = "User with id " + newUserId + " was not found in the database.";
                    LOGGER.error(errorMessage);
                    return new ResourceNotFoundException(errorMessage);
                });

        User currentUser = device.getUser();

        device.setUser(newUser); // Set the new user for the energy meter

        deviceRepository.save(device);
    }

    @Transactional
    public void disassociateUserFromEnergyMeter(Long energyMeterId) {
        Device device = deviceRepository.findById(energyMeterId)
                .orElseThrow(() -> {
                    String errorMessage = "EnergyMeter with id " + energyMeterId + " was not found in the database.";
                    LOGGER.error(errorMessage);
                    return new ResourceNotFoundException(errorMessage);
                });

        User user = device.getUser(); // Get the associated user

        device.setUser(null); // Disassociate the user from the energy meter
        messageProducer.sendDeviceMessage(device,"UPDATE");
        deviceRepository.save(device);
    }
}
