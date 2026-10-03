package disi.savinglives_backend.controllers;

import disi.savinglives_backend.config.MyWebSocketHandler;
import disi.savinglives_backend.dtos.DonationRequestDTO;
import disi.savinglives_backend.entities.DonationRequest;
import disi.savinglives_backend.entities.User;
import disi.savinglives_backend.entities.enums.DonationRequestStatus;
import disi.savinglives_backend.services.DonationRequestService;
import disi.savinglives_backend.services.UserService;
import lombok.AllArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/dr")
@AllArgsConstructor
@CrossOrigin
public class DonationRequestController {

    private DonationRequestService donationRequestService;
    private final MyWebSocketHandler myWebSocketHandler;
    private final UserService userService;

    @PostMapping("/create")
    public ResponseEntity<DonationRequest> createDonationRequest(@RequestBody DonationRequestDTO donationRequestDTO) throws IOException {
        DonationRequest donationRequest = donationRequestService.createOrUpdateDonationRequest(donationRequestDTO);
        myWebSocketHandler.broadcastMessage();
        return ResponseEntity.ok(donationRequest);
    }

    @GetMapping("/fetch-all")
    public ResponseEntity<List<DonationRequest>> getAllDonationRequests() {
        List<DonationRequest> requests = donationRequestService.findAllDonationRequests();
        return ResponseEntity.ok(requests);
    }

    @GetMapping("/fetch-all/{userId}")
    public ResponseEntity<List<DonationRequest>> getAllDonationRequests(@PathVariable UUID userId) {
        User user = userService.findUserById(userId);
        if (user != null) {
            List<DonationRequest> requests = donationRequestService.findAllRequestByUserMatch(user.getCity(), user.getBloodGroup());
            return ResponseEntity.ok(requests);
        }
        return ResponseEntity.ok(null);
    }

    @GetMapping("/{id}")
    public ResponseEntity<DonationRequest> getDonationRequest(@PathVariable UUID id) {
        DonationRequest request = donationRequestService.findDonationRequestById(id);
        return ResponseEntity.ok(request);
    }

    @PutMapping("/{id}/status/{userId}")
    public ResponseEntity<?> updateDonationRequestStatus(@PathVariable UUID id, @PathVariable UUID userId) {
        boolean updatedRequest = donationRequestService.updateDonationRequestStatus(id, userId);
        return ResponseEntity.ok(updatedRequest);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteDonationRequest(@PathVariable UUID id) {
        donationRequestService.deleteDonationRequest(id);
        return ResponseEntity.ok().build();
    }
}
