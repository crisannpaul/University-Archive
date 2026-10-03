package com.example.em_microservice.dto.builder;

import com.example.em_microservice.dto.DeviceDTO;
import com.example.em_microservice.dto.DeviceMessageDTO;
import com.example.em_microservice.model.Device;

public class EnergyMeterBuilder {

    private EnergyMeterBuilder() {
    }

    public static DeviceDTO toEnergyMeterDTO(Device device) {
        DeviceDTO deviceDTO = new DeviceDTO();
        deviceDTO.setName(device.getName());
        deviceDTO.setMaxHourlyRate(device.getMaxHourlyRate());

        // Convert the associated User entity to UserDTO
        if (device.getUser() != null) {
            deviceDTO.setUser(device.getUser());
        }

        return deviceDTO;
    }

    public static Device toEntity(DeviceDTO deviceDTO) {
        Device device = new Device();
        device.setName(deviceDTO.getName());
        device.setMaxHourlyRate(deviceDTO.getMaxHourlyRate());

        if (deviceDTO.getUser() != null) {
            device.setUser(deviceDTO.getUser());
        }

        return device;
    }
}

