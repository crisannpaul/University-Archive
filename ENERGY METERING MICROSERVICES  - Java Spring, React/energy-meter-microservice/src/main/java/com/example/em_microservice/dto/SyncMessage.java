package com.example.em_microservice.dto;

import com.example.em_microservice.model.Device;

import java.io.Serializable;

public class SyncMessage implements Serializable {
    private String command;
    private DeviceMessageDTO device;

    public SyncMessage() {
    }

    public SyncMessage(String command, DeviceMessageDTO device) {
        this.command = command;
        this.device = device;
    }

    public String getCommand() {
        return command;
    }

    public void setCommand(String command) {
        this.command = command;
    }

    public DeviceMessageDTO getEnergyMeter() {
        return device;
    }

    public void setEnergyMeter(DeviceMessageDTO device) {
        this.device = device;
    }
}
