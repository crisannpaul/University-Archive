package com.example.communication_microservice.service;

import com.example.communication_microservice.model.NotificationMessage;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

@Service
public class NotificationService {

    @Autowired
    private final SimpMessagingTemplate template;

    @Autowired
    public NotificationService(SimpMessagingTemplate template) {
        this.template = template;
    }

    public void sendNotification(Long userId, String notification) {
        template.convertAndSend("/topic/user." + userId, notification);
    }
}
