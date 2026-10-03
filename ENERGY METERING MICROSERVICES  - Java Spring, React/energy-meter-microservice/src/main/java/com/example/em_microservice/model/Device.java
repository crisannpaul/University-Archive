package com.example.em_microservice.model;

import jakarta.persistence.*;

import java.io.Serializable;

@Entity
@Table(name = "energy_meters")
public class Device implements Serializable{
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "em_id")
    private Long energyMeterId;

    @Column(name = "em_name")
    private String name;

    @Column(name = "max_hourly_rate")
    private Double maxHourlyRate;

    @ManyToOne
    @JoinColumn(name = "user_id")
    private User user;

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

    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }
}
