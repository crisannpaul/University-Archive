package com.example.em_microservice.controller;

import com.example.em_microservice.controller.handlers.exceptions.ResourceNotFoundException;
import com.example.em_microservice.dto.DeviceUserDTO;
import com.example.em_microservice.service.DeviceUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@CrossOrigin
@RequestMapping(value = "/api/em-user")
public class DeviceUserController {
    @Autowired
    private DeviceUserService energyMeterUserService;

    @PostMapping("/map")
    public ResponseEntity<Void> mapUserToEnergyMeter(@RequestBody DeviceUserDTO mappingDTO) {
        try {
            energyMeterUserService.associateUserWithEnergyMeter(mappingDTO.getEmId(), mappingDTO.getUserId());
            return new ResponseEntity<>(HttpStatus.OK);
        } catch (ResourceNotFoundException e) {
            System.out.println(e.getMessage());
            return new ResponseEntity<>(e.getStatus());
        }
    }

    @DeleteMapping("/unmap")
    public ResponseEntity<Void> unmapUserToEnergyMeter(@RequestBody DeviceUserDTO mappingDTO) {
        try {
            energyMeterUserService.disassociateUserFromEnergyMeter(mappingDTO.getEmId());
            return new ResponseEntity<>(HttpStatus.OK);
        } catch (ResourceNotFoundException e) {
            System.out.println(e.getMessage());
            return new ResponseEntity<>(e.getStatus());
        }
    }
}
