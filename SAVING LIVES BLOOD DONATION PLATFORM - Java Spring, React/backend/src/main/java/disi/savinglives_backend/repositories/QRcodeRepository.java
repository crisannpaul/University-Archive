package disi.savinglives_backend.repositories;

import disi.savinglives_backend.entities.AnalysisResult;
import disi.savinglives_backend.entities.InformativeContent;
import disi.savinglives_backend.entities.QRcode;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.UUID;

public interface QRcodeRepository extends JpaRepository<QRcode, UUID> {

    @Override
    List<QRcode> findAll();

    List<QRcode> findByUserId(String userId);

}
