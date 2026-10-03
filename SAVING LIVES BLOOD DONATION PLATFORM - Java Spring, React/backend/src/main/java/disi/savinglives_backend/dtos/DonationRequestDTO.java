package disi.savinglives_backend.dtos;

import lombok.Data;
import java.util.UUID;

@Data
public class DonationRequestDTO {

    private UUID id;  // Optional, depends if you need to expose this in the DTO
    private UUID userId;
    private UUID donationCenterId;
    private String status; // e.g., pending, completed

    // Default constructor
    public DonationRequestDTO() {
    }

    // Constructor with all fields
    public DonationRequestDTO(UUID id, UUID userId, UUID donationCenterId, String status) {
        this.id = id;
        this.userId = userId;
        this.donationCenterId = donationCenterId;
        this.status = status;
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public UUID getUserId() {
        return userId;
    }

    public void setUserId(UUID userId) {
        this.userId = userId;
    }

    public UUID getDonationCenterId() {
        return donationCenterId;
    }

    public void setDonationCenterId(UUID donationCenterId) {
        this.donationCenterId = donationCenterId;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}
