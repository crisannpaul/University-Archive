package com.example.communication_microservice.model;

import jakarta.persistence.*;
import java.util.Date;

@Entity
public class EnergyData {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Long id;

    @Column(nullable = false)
    private Date timestamp;

    @Column(nullable = false)
    private Long deviceId;

    @Column(nullable = false)
    private Double value;

    public EnergyData(Long id, Date timestamp, Long deviceId, Double value) {
        this.id = id;
        this.timestamp = timestamp;
        this.deviceId = deviceId;
        this.value = value;
    }

    public EnergyData() {

    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Date getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(Date timestamp) {
        this.timestamp = timestamp;
    }

    public Long getDeviceId() {
        return deviceId;
    }

    public void setDeviceId(Long deviceId) {
        this.deviceId = deviceId;
    }

    public Double getValue() {
        return value;
    }

    public void setValue(Double value) {
        this.value = value;
    }

    @Override
    public String toString() {
        return "Message{" +
                "id=" + id +
                ", timestamp=" + timestamp +
                ", deviceId='" + deviceId + '\'' +
                ", value=" + value +
                '}';
    }
}
