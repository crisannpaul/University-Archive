package com.example.communication_microservice.repository;

import com.example.communication_microservice.model.HourlyConsumption;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Date;
import java.util.List;

@Repository
public interface HourlyConsumptionRepository extends JpaRepository<HourlyConsumption, Long> {
    List<HourlyConsumption> findByDevice_UserIdAndTimestampBetween(Long userId, Date timestampStart, Date timestampEnd);

    List<HourlyConsumption> findByDevice_UserId(Long userId);


}
