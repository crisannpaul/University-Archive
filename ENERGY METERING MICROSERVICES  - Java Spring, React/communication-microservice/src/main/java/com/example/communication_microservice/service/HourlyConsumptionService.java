package com.example.communication_microservice.service;

import com.example.communication_microservice.model.HourlyConsumption;
import com.example.communication_microservice.model.Device;
import com.example.communication_microservice.repository.HourlyConsumptionRepository;
import com.example.communication_microservice.repository.DeviceRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.util.Date;
import java.util.List;

@Service
public class HourlyConsumptionService {

    private final HourlyConsumptionRepository hourlyConsumptionRepository;
    private final DeviceRepository deviceRepository;
    private final EnergyDataService energyDataService;
    private final NotificationService notificationService;


    @Autowired
    public HourlyConsumptionService(HourlyConsumptionRepository hourlyConsumptionRepository,
                                    DeviceRepository deviceRepository,
                                    EnergyDataService energyDataService, NotificationService notificationService) {
        this.hourlyConsumptionRepository = hourlyConsumptionRepository;
        this.deviceRepository = deviceRepository;
        this.energyDataService = energyDataService;
        this.notificationService = notificationService;
    }

    @Scheduled(fixedRate = 6000)
    public void calculateHourlyConsumption() {
        System.out.println("Checking");
        List<Device> devices = deviceRepository.findAll();

        for (Device device : devices) {
            Double totalConsumption = energyDataService.calculateTotalConsumption(device.getEnergyMeterId());

            boolean exceedsMaxRate = totalConsumption > device.getMaxHourlyRate();
            System.out.println("Device: " + device.getEnergyMeterId() + " - " + totalConsumption + "\nExceeds: " + exceedsMaxRate);

            HourlyConsumption consumption = new HourlyConsumption();
            consumption.setDevice(device);
            consumption.setTimestamp(new Date());
            consumption.setTotalConsumption(totalConsumption);
            hourlyConsumptionRepository.save(consumption);

            if (exceedsMaxRate) {
                String notification = "Device " + device.getName() + " exceeded max hourly rate. Consumption = " + totalConsumption;
                notificationService.sendNotification(device.getUserId(), notification);
            }
        }
    }
}
