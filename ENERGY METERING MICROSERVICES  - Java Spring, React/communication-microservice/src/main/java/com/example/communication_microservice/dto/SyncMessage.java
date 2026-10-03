package com.example.communication_microservice.dto;

import com.example.communication_microservice.model.Device;

import java.io.Serializable;

public class SyncMessage implements Serializable {
    private String command;
    private Device device;

    public SyncMessage() {
    }

    public SyncMessage(String command, Device device) {
        this.command = command;
        this.device = device;
    }

    public String getCommand() {
        return command;
    }

    public void setCommand(String command) {
        this.command = command;
    }

    public Device getEnergyMeter() {
        return device;
    }

    public void setEnergyMeter(Device device) {
        this.device = device;
    }
}
