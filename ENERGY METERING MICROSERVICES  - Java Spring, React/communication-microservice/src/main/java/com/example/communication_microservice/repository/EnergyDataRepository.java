package com.example.communication_microservice.repository;

import com.example.communication_microservice.model.EnergyData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Date;
import java.util.List;

@Repository
public interface EnergyDataRepository extends JpaRepository<EnergyData, Long> {
    List<EnergyData> findByDeviceId(Long deviceId);

    List<EnergyData> findByDeviceIdAndTimestampBetween(Long deviceId, Date timestampStart, Date timestampEnd);

    List<EnergyData> findTop6ByDeviceIdOrderByTimestampDesc(Long id);


}
