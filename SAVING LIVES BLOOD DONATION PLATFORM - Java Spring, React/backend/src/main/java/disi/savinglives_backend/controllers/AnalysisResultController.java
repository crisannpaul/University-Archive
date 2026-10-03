package disi.savinglives_backend.controllers;

import disi.savinglives_backend.dtos.AnalysisResultDTO;
import disi.savinglives_backend.entities.AnalysisResult;
import disi.savinglives_backend.services.AnalysisResultService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping(value = "/api/v1/analysisresult")
@CrossOrigin
public class AnalysisResultController {

    private final AnalysisResultService analysisResultService;

    @PostMapping(value = "/create")
    public ResponseEntity<?> createAnalysisResult(@RequestBody AnalysisResultDTO analysisResult) {
        AnalysisResult createdResult = analysisResultService.create(analysisResult);
        return ResponseEntity.ok(createdResult);
    }

    @GetMapping(value = "/user/{userId}")
    public ResponseEntity<?> getAnalysisResultsByUserId(@PathVariable String userId) {
        List<AnalysisResult> results = analysisResultService.getByUserId(userId);
        return ResponseEntity.ok(results);
    }

    @GetMapping(value = "/user/get_last/{userId}")
    public ResponseEntity<?> getLastAnalysisResultsByUserId(@PathVariable String userId) {
        AnalysisResult results = analysisResultService.getLastByUserId(userId);
        Integer timestamp = -1;
        if (results != null)

            
            timestamp = Math.round((float) results.getTimestamp().getTime() / 1000);
        return ResponseEntity.ok(timestamp);
    }

}
