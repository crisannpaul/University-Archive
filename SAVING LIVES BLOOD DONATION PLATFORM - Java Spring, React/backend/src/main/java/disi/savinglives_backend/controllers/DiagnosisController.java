package disi.savinglives_backend.controllers;

import disi.savinglives_backend.services.DiagnosisService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/diagnosis")
@Validated
@CrossOrigin
public class DiagnosisController {

    @Autowired
    private DiagnosisService diagnosisService;

    @PostMapping("/get")
    public ResponseEntity<String> getDiagnosis(@RequestBody String symptoms) {
        try {
            String diagnosis = diagnosisService.getDiagnosis(symptoms);
            return new ResponseEntity<>(diagnosis, HttpStatus.OK);
        } catch (Exception e) {
            return new ResponseEntity<>("Diagnosis service is unavailable. Please try again later.", HttpStatus.SERVICE_UNAVAILABLE);
        }
    }
}