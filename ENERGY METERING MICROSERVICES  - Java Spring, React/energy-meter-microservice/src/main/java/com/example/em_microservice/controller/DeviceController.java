package com.example.em_microservice.controller;

import com.example.em_microservice.dto.DeviceDTO;
import com.example.em_microservice.dto.builder.EnergyMeterBuilder;
import com.example.em_microservice.model.Device;
import com.example.em_microservice.service.DeviceService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@CrossOrigin
@RequestMapping(value = "/api/energy-meter")
public class DeviceController {

    private final DeviceService deviceService;

    @Autowired
    public DeviceController(DeviceService deviceService) {
        this.deviceService = deviceService;
    }


    @GetMapping()
    public ResponseEntity<List<Device>> getEnergyMeters() {
        List<Device> dtos = deviceService.findEnergyMeters();
        return new ResponseEntity<>(dtos, HttpStatus.OK);
    }

    @GetMapping("/user/{id}")
    public ResponseEntity<List<Device>> getEnergyMetersByUserId(@PathVariable("id") Long userId) {
        List<Device> dtos = deviceService.findEnergyMetersByUserId(userId);
        return new ResponseEntity<>(dtos, HttpStatus.OK);
    }

    @PutMapping("/{id}")
    public ResponseEntity<DeviceDTO> updateUser(@PathVariable Long id, @RequestBody DeviceDTO updatedEm) {
        DeviceDTO updatedUserData = EnergyMeterBuilder.toEnergyMeterDTO(deviceService.update(id, updatedEm));

        return new ResponseEntity<>(updatedUserData, HttpStatus.OK);
    }

    @PostMapping()
    public ResponseEntity<Long> insertEnergyMeter(@RequestBody DeviceDTO energyMeter) {
        Long energyMeterId = deviceService.insert(energyMeter);
        return new ResponseEntity<>(energyMeterId, HttpStatus.CREATED);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteEnergyMeter(@PathVariable Long id) {
        deviceService.delete(id);

        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }

    @GetMapping(value = "/{id}")
    public ResponseEntity<DeviceDTO> getEnergyMeter(@PathVariable("id") Long energyMeterId) {
        DeviceDTO dto = deviceService.findEnergyMeterById(energyMeterId);
        return new ResponseEntity<>(dto, HttpStatus.OK);
    }
}


