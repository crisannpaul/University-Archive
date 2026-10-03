package com.example.communication_microservice.compnents;

import com.example.communication_microservice.model.EnergyData;
import com.example.communication_microservice.service.EnergyDataService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.amqp.core.Message;
import org.springframework.amqp.core.MessageListener;
import org.springframework.stereotype.Service;

import java.io.IOException;

@Service
public class DataMessageBroker implements MessageListener {

    private final EnergyDataService energyDataService;

    public DataMessageBroker(EnergyDataService energyDataService) {
        this.energyDataService = energyDataService;
    }

    @Override
    public void onMessage(Message message) {
        try {
            ObjectMapper objectMapper = new ObjectMapper();

            // Assuming the body of the message is a JSON string
            String jsonMessage = new String(message.getBody());
            System.out.println("Received message: " + jsonMessage);

            // Convert JSON string to EnergyData object
            EnergyData energyData = objectMapper.readValue(jsonMessage, EnergyData.class);

            // Save the EnergyData object using the service
            energyDataService.createMessage(energyData.getTimestamp(), energyData.getDeviceId(), energyData.getValue());
        } catch (IOException e) {
            // Handle the exception properly - this could be logging or even requeuing the message
            System.err.println("Failed to convert message to EnergyData object: " + e.getMessage());
        }
    }
}
