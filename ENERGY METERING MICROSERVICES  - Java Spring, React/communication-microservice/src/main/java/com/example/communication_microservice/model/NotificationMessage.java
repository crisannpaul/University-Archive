package com.example.communication_microservice.model;

public class NotificationMessage {
    private Long userId;
    private String message;

    public NotificationMessage(Long userId, String message) {
        this.userId = userId;
        this.message = message;
    }

    public NotificationMessage() {
    }

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
