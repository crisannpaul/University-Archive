package disi.savinglives_backend.services;

import disi.savinglives_backend.controllers.handlers.exceptions.model.ResourceNotFoundException;
import disi.savinglives_backend.dtos.DonationRequestDTO;
import disi.savinglives_backend.entities.AnalysisResult;
import disi.savinglives_backend.entities.DonationCenter;
import disi.savinglives_backend.entities.DonationRequest;
import disi.savinglives_backend.entities.User;
import disi.savinglives_backend.entities.enums.BloodGroup;
import disi.savinglives_backend.entities.enums.DonationRequestStatus;
import disi.savinglives_backend.repositories.DonationCenterRepository;
import disi.savinglives_backend.repositories.DonationRequestRepository;
import disi.savinglives_backend.repositories.UserRepository;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
@RequiredArgsConstructor
public class DonationRequestService {
    private static final Logger LOGGER = LoggerFactory.getLogger(DonationRequestService.class);
    private final DonationRequestRepository donationRequestRepository;
    private final UserRepository userRepository;
    private final DonationCenterRepository donationCenterRepository;
    private final AnalysisResultService analysisResultService;

    private final QRcodeService qRcodeService;

    public DonationRequest createOrUpdateDonationRequest(DonationRequestDTO dto) {
        User user = userRepository.findById(dto.getUserId())
                .orElseThrow(() -> new ResourceNotFoundException("User with ID " + dto.getUserId() + " not found"));
        DonationCenter donationCenter = donationCenterRepository.findById(dto.getDonationCenterId())
                .orElseThrow(() -> new ResourceNotFoundException("Donation Center with ID " + dto.getDonationCenterId() + " not found"));

        DonationRequest donationRequest = dto.getId() != null ? donationRequestRepository.findById(dto.getId()).orElse(new DonationRequest()) : new DonationRequest();
        donationRequest.setUser(user);
        donationRequest.setDonationCenter(donationCenter);
        donationRequest.setStatus(DonationRequestStatus.valueOf(dto.getStatus()));
        return donationRequestRepository.save(donationRequest);
    }

    public List<DonationRequest> findAllDonationRequests() {
        return donationRequestRepository.findAll();
    }

    public DonationRequest findDonationRequestById(UUID id) {
        return donationRequestRepository.findById(id).orElseThrow(() -> new ResourceNotFoundException("DonationRequest with ID " + id + " not found"));
    }

    public void deleteDonationRequest(UUID id) {
        donationRequestRepository.deleteById(id);
    }

    public boolean updateDonationRequestStatus(UUID id, UUID userId) {
        DonationRequest donationRequest = findDonationRequestById(id);
        AnalysisResult analysisResult = analysisResultService.getLastByUserId(String.valueOf(userId));
        Date now = new Date();
        if (analysisResult.getEligibility().equals("false") || (now.getTime() / 1000) - 120 < Math.round((float) analysisResult.getTimestamp().getTime() / 1000))
            return false;
        donationRequest.setStatus(DonationRequestStatus.COMPLETE);
        qRcodeService.create(donationRequest);
        donationRequestRepository.save(donationRequest);
        return true;
    }

    public List<User> findAllMatchUsers(String city, BloodGroup bloodGroup) {

        List<DonationRequest> requestList = donationRequestRepository.findAll();
        List<User> list = new ArrayList<>();
        for (DonationRequest donationRequest: requestList) {


            if (donationRequest.getDonationCenter().getCity().equals(city) &&
            donationRequest.getUser().getBloodGroup().equals(bloodGroup))
                list.add(donationRequest.getUser());
        }


        return list;
    }

    public List<DonationRequest> findAllRequestByUserMatch(String city, BloodGroup bloodGroup) {

        List<DonationRequest> requestList = donationRequestRepository.findAll();
        List<DonationRequest> list = new ArrayList<>();
        for (DonationRequest donationRequest: requestList) {
            if (donationRequest.getDonationCenter().getCity().equals(city) &&
                    donationRequest.getUser().getBloodGroup().equals(bloodGroup))
                list.add(donationRequest);
        }


        return list;
    }
}
