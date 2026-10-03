package com.example.em_microservice.components;

import com.example.em_microservice.dto.DeviceMessageDTO;
import com.example.em_microservice.dto.SyncMessage;
import com.example.em_microservice.model.Device;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.fasterxml.jackson.databind.ObjectMapper;

@Service
public class MessageProducer {

    private final RabbitTemplate rabbitTemplate;

    @Autowired
    public MessageProducer(RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    public void sendDeviceMessage(Device device, String operationType) {
        try {
            ObjectMapper objectMapper = new ObjectMapper();
            DeviceMessageDTO messageDTO = DeviceMessageDTO.toDeviceMessageDTO(device);
            SyncMessage syncMessage = new SyncMessage(operationType, messageDTO);
            String syncMessageJson = objectMapper.writeValueAsString(syncMessage);
            rabbitTemplate.convertAndSend("", "device_sync", syncMessageJson);
            System.out.println(syncMessageJson);
        } catch (Exception e) {
            throw new RuntimeException("Could not send device sync message", e);
        }
    }
}
