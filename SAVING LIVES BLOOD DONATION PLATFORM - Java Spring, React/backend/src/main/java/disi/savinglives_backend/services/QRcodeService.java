package disi.savinglives_backend.services;


import disi.savinglives_backend.entities.DonationRequest;
import disi.savinglives_backend.entities.QRcode;
import disi.savinglives_backend.repositories.InformativeContentRepository;
import disi.savinglives_backend.repositories.QRcodeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class QRcodeService {

    private final QRcodeRepository qRcodeRepository;

    public void create(DonationRequest donationRequest){
        QRcode code = new QRcode();
        code.setUserId(donationRequest.getUser().getId().toString());
        code.setTitle(donationRequest.getUser().getName());
        code.setQr_sting(donationRequest.getUser().getName());
        qRcodeRepository.save(code);
    }

    public List<QRcode> getCodesForUser(String id){
        return qRcodeRepository.findByUserId(id);
    }



}
