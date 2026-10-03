package disi.savinglives_backend.repositories;

import disi.savinglives_backend.entities.AnalysisResult;
import disi.savinglives_backend.entities.InformativeContent;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface AnalysisResultRepository extends JpaRepository<AnalysisResult, UUID> {
    List<AnalysisResult> findByUserId(String userId);
    AnalysisResult findTop1ByUserIdOrderByTimestampDesc(String userId);
}
