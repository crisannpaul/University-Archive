package com.example.em_microservice.dto;

import com.example.em_microservice.model.Device;

import java.io.Serializable;

public class DeviceMessageDTO implements Serializable {
    private Long energyMeterId;
    private String name;
    private Double maxHourlyRate;
    private Long userId; // Replaces the User object with just the user ID

    // Constructors, getters, setters

    public DeviceMessageDTO() {
    }

    public DeviceMessageDTO(Long energyMeterId, String name, Double maxHourlyRate, Long userId) {
        this.energyMeterId = energyMeterId;
        this.name = name;
        this.maxHourlyRate = maxHourlyRate;
        this.userId = userId;
    }

    public static DeviceMessageDTO toDeviceMessageDTO(Device device) {
        if (device == null) {
            return null;
        }
        DeviceMessageDTO dto = new DeviceMessageDTO();
        dto.setEnergyMeterId(device.getEnergyMeterId());
        dto.setName(device.getName());
        dto.setMaxHourlyRate(device.getMaxHourlyRate());
        dto.setUserId(device.getUser() != null ? device.getUser().getUserId() : null);
        return dto;
    }

    public Long getEnergyMeterId() {
        return energyMeterId;
    }

    public void setEnergyMeterId(Long energyMeterId) {
        this.energyMeterId = energyMeterId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Double getMaxHourlyRate() {
        return maxHourlyRate;
    }

    public void setMaxHourlyRate(Double maxHourlyRate) {
        this.maxHourlyRate = maxHourlyRate;
    }

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

}

