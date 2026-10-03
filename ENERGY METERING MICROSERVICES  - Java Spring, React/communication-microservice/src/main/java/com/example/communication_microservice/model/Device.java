package com.example.communication_microservice.model;

import jakarta.persistence.*;

import java.io.Serializable;

@Entity
@Table(name = "energy_meters")
public class Device implements Serializable{
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long energyMeterId;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private Double maxHourlyRate;

    @Column(nullable = true)
    private Long userId;

    public Long getEnergyMeterId() {
        return energyMeterId;
    }

    public void setEnergyMeterId(Long energyMeterId) {
        this.energyMeterId = energyMeterId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Double getMaxHourlyRate() {
        return maxHourlyRate;
    }

    public void setMaxHourlyRate(Double maxHourlyRate) {
        this.maxHourlyRate = maxHourlyRate;
    }

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }
}
