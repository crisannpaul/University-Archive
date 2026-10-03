package com.example.communication_microservice.service;

import com.example.communication_microservice.model.EnergyData;
import com.example.communication_microservice.repository.EnergyDataRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class EnergyDataService {

    private final EnergyDataRepository energyDataRepository;

    private final DeviceService deviceService;

    @Autowired
    public EnergyDataService(EnergyDataRepository energyDataRepository, DeviceService deviceService) {
        this.energyDataRepository = energyDataRepository;
        this.deviceService = deviceService;
    }

    @Transactional
    public EnergyData createMessage(Date timestamp, Long deviceId, Double value) {
        EnergyData energyData = new EnergyData();
        energyData.setTimestamp(timestamp);
        energyData.setDeviceId(deviceId);
        energyData.setValue(value);
        return energyDataRepository.save(energyData);
    }

    public Map<Integer, Double> getDailyConsumptionForUser(Long userId, LocalDate date) {
        List<Long> deviceIds = deviceService.getDeviceIdsForUser(userId);

        Date startOfDay = java.sql.Timestamp.valueOf(date.atStartOfDay());
        Date endOfDay = java.sql.Timestamp.valueOf(date.atTime(23, 59, 59));

        Map<Integer, Double> consumptionByHour = new TreeMap<>();
        for (Long deviceId : deviceIds) {
            List<EnergyData> energyDataList = energyDataRepository.findByDeviceIdAndTimestampBetween(deviceId, startOfDay, endOfDay);

            Map<Integer, Double> deviceConsumption = energyDataList.stream()
                    .collect(Collectors.groupingBy(
                            data -> getHourFromTimestamp(data.getTimestamp()),
                            TreeMap::new,
                            Collectors.summingDouble(EnergyData::getValue)));

            deviceConsumption.forEach((hour, consumption) ->
                    consumptionByHour.merge(hour, consumption, Double::sum));
        }

        // Ensure all hours are represented in the map
        for (int hour = 0; hour < 24; hour++) {
            consumptionByHour.putIfAbsent(hour, 0.0);
        }

        return consumptionByHour;
    }

    private int getHourFromTimestamp(Date timestamp) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(timestamp);
        return calendar.get(Calendar.HOUR_OF_DAY);
    }

    public Double calculateTotalConsumption(Long deviceId) {
        // Fetch the last 6 energy data entries for the device, sorted by timestamp
        List<EnergyData> energyDataList = energyDataRepository.findTop6ByDeviceIdOrderByTimestampDesc(deviceId);

        // Aggregate the total consumption
        double totalConsumption = 0.0;
        for (EnergyData data : energyDataList) {
            totalConsumption += data.getValue(); // Assuming 'getValue()' returns the consumption value
        }

        return totalConsumption;
    }
    public Optional<EnergyData> getMessageById(Long id) {
        return energyDataRepository.findById(id);
    }

    public List<EnergyData> getAllMessages() {
        return energyDataRepository.findAll();
    }

    @Transactional
    public EnergyData updateMessage(Long id, Date timestamp, Long deviceId, Double value) {
        EnergyData energyData = energyDataRepository.findById(id)
                .orElseThrow(() -> new IllegalStateException(
                        "Message with id " + id + " does not exist."
                ));
        energyData.setTimestamp(timestamp);
        energyData.setDeviceId(deviceId);
        energyData.setValue(value);
        return energyDataRepository.save(energyData);
    }

    @Transactional
    public void deleteMessage(Long id) {
        boolean exists = energyDataRepository.existsById(id);
        if (!exists) {
            throw new IllegalStateException("Message with id " + id + " does not exist.");
        }
        energyDataRepository.deleteById(id);
    }

    // Additional methods to process messages and handle business logic
}
