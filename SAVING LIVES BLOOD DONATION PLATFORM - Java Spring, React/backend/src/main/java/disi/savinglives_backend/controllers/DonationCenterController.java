package disi.savinglives_backend.controllers;

import disi.savinglives_backend.dtos.AuthDTO;
import disi.savinglives_backend.dtos.DonationCenterDTO;
import disi.savinglives_backend.dtos.LoginDTO;
import disi.savinglives_backend.entities.DonationCenter;
import disi.savinglives_backend.entities.User;
import disi.savinglives_backend.repositories.DonationCenterRepository;
import disi.savinglives_backend.security.JwtUtils;
import disi.savinglives_backend.services.DonationCenterService;
import disi.savinglives_backend.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping(value = "/api/v1/dc")
@RequiredArgsConstructor
@CrossOrigin
public class DonationCenterController {
    private final DonationCenterService donationCenterService;
    private final DonationCenterRepository donationCenterRepository;

    @PostMapping("/create")
    public ResponseEntity<UUID> createDonationCenter(@RequestBody DonationCenterDTO donationCenterDTO) {

        UUID id = donationCenterService.insert(donationCenterDTO);
        if (id!=null)
            return ResponseEntity.ok(id);
        return new ResponseEntity<>(null, HttpStatus.METHOD_FAILURE);
    }

    @GetMapping("/all")
    public ResponseEntity<?> getAllDonationCenters(){
        return ResponseEntity.ok(donationCenterService.findAllDonationCenters());
    }
}
