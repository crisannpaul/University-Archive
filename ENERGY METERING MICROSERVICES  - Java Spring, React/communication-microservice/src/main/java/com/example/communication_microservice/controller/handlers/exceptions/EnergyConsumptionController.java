package com.example.communication_microservice.controller.handlers.exceptions;

import com.example.communication_microservice.service.EnergyDataService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDate;
import java.util.Map;

@RestController
@RequestMapping("/api/energy-consumption")
@CrossOrigin
public class EnergyConsumptionController {

    @Autowired
    private EnergyDataService energyDataService;

    @GetMapping("/{userId}/{date}")
    public ResponseEntity<Map<Integer, Double>> getDailyConsumption(
            @PathVariable Long userId,
            @PathVariable @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {

        try {
            Map<Integer, Double> consumptionData = energyDataService.getDailyConsumptionForUser(userId, date);
            return new ResponseEntity<>(consumptionData, HttpStatus.OK);
        } catch (Exception e) {
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }
}
