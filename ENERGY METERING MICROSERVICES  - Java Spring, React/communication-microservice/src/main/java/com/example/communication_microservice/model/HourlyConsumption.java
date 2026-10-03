package com.example.communication_microservice.model;

import jakarta.persistence.*;

import java.io.Serializable;
import java.util.Date;

@Entity
@Table(name = "hourly_consumption")
public class HourlyConsumption implements Serializable {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    @Temporal(TemporalType.TIMESTAMP)
    private Date timestamp; // To store the hour of the consumption

    @Column(nullable = false)
    private Double totalConsumption; // Total energy consumption for the hour

    @ManyToOne
    @JoinColumn(name = "energy_meter_id", nullable = false)
    private Device device; // Relation to Device

    // Constructors, getters, and setters

    public HourlyConsumption() {
    }

    public HourlyConsumption(Date timestamp, Double totalConsumption, Device device) {
        this.timestamp = timestamp;
        this.totalConsumption = totalConsumption;
        this.device = device;

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

    public Double getTotalConsumption() {
        return totalConsumption;
    }

    public void setTotalConsumption(Double totalConsumption) {
        this.totalConsumption = totalConsumption;
    }

    public Device getDevice() {
        return device;
    }

    public void setDevice(Device device) {
        this.device = device;
    }
}
