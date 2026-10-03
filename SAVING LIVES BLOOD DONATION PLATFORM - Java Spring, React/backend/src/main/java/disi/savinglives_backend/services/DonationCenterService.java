package disi.savinglives_backend.services;


import disi.savinglives_backend.dtos.DonationCenterDTO;
import disi.savinglives_backend.entities.DonationCenter;
import disi.savinglives_backend.repositories.DonationCenterRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

@Service
public class DonationCenterService {

    @Autowired
    DonationCenterRepository donationCenterRepository;

    public UUID insert(DonationCenterDTO donationCenterDTO){
        DonationCenter dc = new DonationCenter();
        dc.setName(donationCenterDTO.getName());
        dc.setCity(donationCenterDTO.getCity());
        dc.setCountry(donationCenterDTO.getCountry());
        dc.setRegion(donationCenterDTO.getRegion());
        dc.setStreetNumber(donationCenterDTO.getStreetNumber());
        dc.setStreet(donationCenterDTO.getStreet());
        if (donationCenterDTO.getLatitude() != null)
            dc.setLatitude(donationCenterDTO.getLatitude());
        if (donationCenterDTO.getLongitude() != null)
            dc.setLongitude(donationCenterDTO.getLongitude());
        donationCenterRepository.save(dc);
        return dc.getId();
    }

    public List<DonationCenter> findAllDonationCenters() {
        return donationCenterRepository.findAll();
    }
}
