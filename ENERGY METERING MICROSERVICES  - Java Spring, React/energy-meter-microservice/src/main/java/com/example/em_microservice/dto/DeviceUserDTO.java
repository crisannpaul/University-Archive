package com.example.em_microservice.dto;

public class DeviceUserDTO {
    private Long emId;
    private Long userId;

    public DeviceUserDTO(Long emId, Long userId) {
        this.emId = emId;
        this.userId = userId;
    }

    public DeviceUserDTO() {
    }

    public Long getEmId() {
        return emId;
    }

    public void setEmId(Long emId) {
        this.emId = emId;
    }

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }
}
