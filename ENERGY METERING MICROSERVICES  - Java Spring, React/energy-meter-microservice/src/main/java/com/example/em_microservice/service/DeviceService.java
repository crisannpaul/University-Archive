package com.example.em_microservice.service;

import com.example.em_microservice.components.MessageProducer;
import com.example.em_microservice.controller.handlers.exceptions.ResourceNotFoundException;
import com.example.em_microservice.dto.DeviceDTO;
import com.example.em_microservice.dto.DeviceMessageDTO;
import com.example.em_microservice.dto.builder.EnergyMeterBuilder;
import com.example.em_microservice.model.Device;
import com.example.em_microservice.repository.DeviceRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class DeviceService {
    private static final Logger LOGGER = LoggerFactory.getLogger(DeviceService.class);
    private final DeviceRepository deviceRepository;
    private final MessageProducer messageProducer;

    @Autowired
    public DeviceService(DeviceRepository deviceRepository, MessageProducer messageProducer) {
        this.deviceRepository = deviceRepository;
        this.messageProducer = messageProducer;
    }

    public List<Device> findEnergyMeters() {
        return deviceRepository.findAll();
    }

    public List<Device> findEnergyMetersByUserId(Long userId) {
        return deviceRepository.findByUser_UserId(userId);
    }

    public Device update(Long energyMeterId, DeviceDTO updatedEnergyMeter) {
        Device existingEm = deviceRepository.findById(energyMeterId)
                .orElseThrow(() -> new ResourceNotFoundException("Energy Meter not found with id: " + energyMeterId));

        existingEm.setName(updatedEnergyMeter.getName());
        existingEm.setMaxHourlyRate(updatedEnergyMeter.getMaxHourlyRate());

        return deviceRepository.save(existingEm);
    }

    public void delete(Long emId) {
        Device existingEm = deviceRepository.findById(emId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + emId));

        deviceRepository.delete(existingEm);

        LOGGER.debug("User with id {} was deleted from the database", emId);
    }

    public DeviceDTO findEnergyMeterById(Long id) {
        Optional<Device> energyMeterOptional = deviceRepository.findById(id);
        if (energyMeterOptional.isEmpty()) {
            LOGGER.error("EnergyMeter with id {} was not found in db", id);
            throw new ResourceNotFoundException(Device.class.getSimpleName() + " with id: " + id);
        }
        return EnergyMeterBuilder.toEnergyMeterDTO(energyMeterOptional.get());
    }

    public Long insert(DeviceDTO deviceDTO) {
        Device device = EnergyMeterBuilder.toEntity(deviceDTO);
        device = deviceRepository.save(device);
        LOGGER.debug("EnergyMeter with id {} was inserted in db", device.getEnergyMeterId());
        messageProducer.sendDeviceMessage(device, "CREATE");
        return device.getEnergyMeterId();
    }
}
