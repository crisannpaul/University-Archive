package com.example.em_microservice.dto;

import com.example.em_microservice.model.User;

public class DeviceDTO {
    private String name;
    private Double maxHourlyRate;
    private User user;

    public DeviceDTO(String name, Double maxHourlyRate, User user) {
        this.name = name;
        this.maxHourlyRate = maxHourlyRate;
        this.user = user;
    }

    public DeviceDTO() {

    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public Double getMaxHourlyRate() {
        return maxHourlyRate;
    }

    public void setMaxHourlyRate(Double maxHourlyRate) {
        this.maxHourlyRate = maxHourlyRate;
    }
}
