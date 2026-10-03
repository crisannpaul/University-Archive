package disi.savinglives_backend.controllers;


import disi.savinglives_backend.entities.DonationCenter;
import disi.savinglives_backend.entities.DonationRequest;
import disi.savinglives_backend.entities.QRcode;
import disi.savinglives_backend.services.DonationCenterService;
import disi.savinglives_backend.services.DonationRequestService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.UUID;

@RestController
@RequiredArgsConstructor
@RequestMapping(value = "/api/v1/statistics")
@CrossOrigin
public class StatisticsController {

    private final DonationCenterService donationCenterService;
    private final DonationRequestService donationRequestService;

    @GetMapping(value = "/getCenterRequest")
    public ResponseEntity<?> getAllForUser(@PathVariable UUID id) {
        HashMap<String, Integer> stringMap = new HashMap<>();
        List<DonationCenter> donationCenters = donationCenterService.findAllDonationCenters();
        List<DonationRequest> donationRequests = donationRequestService.findAllDonationRequests();
        for(DonationCenter d : donationCenters)
        {
            int count = 0;
            for (DonationRequest dr: donationRequests)
                if (dr.getDonationCenter().equals(d))
                    count++;
            stringMap.put(d.getName(), count);
        }
        return ResponseEntity.ok(stringMap);
    }
}
