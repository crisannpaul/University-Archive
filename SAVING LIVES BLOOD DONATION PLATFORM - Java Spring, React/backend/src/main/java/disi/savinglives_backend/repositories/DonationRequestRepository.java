package disi.savinglives_backend.repositories;

import disi.savinglives_backend.entities.DonationRequest;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface DonationRequestRepository extends JpaRepository<DonationRequest, UUID> {
}