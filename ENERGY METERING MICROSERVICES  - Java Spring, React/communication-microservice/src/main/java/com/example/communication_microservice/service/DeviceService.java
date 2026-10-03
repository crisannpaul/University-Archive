package com.example.communication_microservice.service;

import com.example.communication_microservice.controller.handlers.exceptions.ResourceNotFoundException;
import com.example.communication_microservice.model.Device;
import com.example.communication_microservice.repository.DeviceRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class DeviceService {
    private static final Logger LOGGER = LoggerFactory.getLogger(DeviceService.class);
    private final DeviceRepository deviceRepository;

    @Autowired
    public DeviceService(DeviceRepository deviceRepository) {
        this.deviceRepository = deviceRepository;
    }

    public List<Device> findEnergyMeters() {
        return deviceRepository.findAll();
    }

    public List<Long> getDeviceIdsForUser(Long userId) {
        return deviceRepository.findByUserId(userId).stream()
                .map(Device::getEnergyMeterId)
                .collect(Collectors.toList());
    }

    public Device update(Long energyMeterId, Device updatedDevice) {
        Device existingEm = deviceRepository.findById(energyMeterId)
                .orElseThrow(() -> new ResourceNotFoundException("Energy Meter not found with id: " + energyMeterId));

        existingEm.setName(updatedDevice.getName());
        existingEm.setMaxHourlyRate(updatedDevice.getMaxHourlyRate());
        existingEm.setUserId(updatedDevice.getUserId());

        return deviceRepository.save(existingEm);
    }

    public void delete(Long emId) {
        Device existingEm = deviceRepository.findById(emId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + emId));

        deviceRepository.delete(existingEm);

        LOGGER.debug("User with id {} was deleted from the database", emId);
    }

    public Device findEnergyMeterById(Long id) {
        Optional<Device> energyMeterOptional = deviceRepository.findById(id);
        if (energyMeterOptional.isEmpty()) {
            LOGGER.error("EnergyMeter with id {} was not found in db", id);
            throw new ResourceNotFoundException(Device.class.getSimpleName() + " with id: " + id);
        }
        return energyMeterOptional.get();
    }

    public Long insert(Device device) {
        device = deviceRepository.save(device);
        LOGGER.debug("EnergyMeter with id {} was inserted in db", device.getEnergyMeterId());
        return device.getEnergyMeterId();
    }
}
