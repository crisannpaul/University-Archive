package com.example.communication_microservice.compnents;

import com.example.communication_microservice.dto.SyncMessage;
import com.example.communication_microservice.model.Device;
import com.example.communication_microservice.service.DeviceService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.amqp.core.Message;
import org.springframework.amqp.core.MessageListener;
import org.springframework.stereotype.Service;

@Service
public class DeviceMessageBroker implements MessageListener {

    private final DeviceService deviceService;

    public DeviceMessageBroker(DeviceService deviceService) {
        this.deviceService = deviceService;
    }

    @Override
    public void onMessage(Message message) {
        try {
            String jsonMessage = new String(message.getBody());
            System.out.println("Received message: " + jsonMessage);

            ObjectMapper objectMapper = new ObjectMapper();
            SyncMessage syncMessage = objectMapper.readValue(jsonMessage, SyncMessage.class);

            switch (syncMessage.getCommand().toUpperCase()) {
                case "CREATE":
                    deviceService.insert(syncMessage.getEnergyMeter());
                    break;
                case "UPDATE":
                    deviceService.update(syncMessage.getEnergyMeter().getEnergyMeterId(), syncMessage.getEnergyMeter());
                    break;
                case "DELETE":
                    deviceService.delete(syncMessage.getEnergyMeter().getEnergyMeterId());
                    break;
                default:
                    System.err.println("Unknown command: " + syncMessage.getCommand());
            }
        } catch (Exception e) {
            System.err.println("Error processing message: " + e.getMessage());
        }
    }
}
