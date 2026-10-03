package disi.savinglives_backend.services;

import disi.savinglives_backend.dtos.AnalysisResultDTO;
import disi.savinglives_backend.entities.AnalysisResult;
import disi.savinglives_backend.repositories.AnalysisResultRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor

public class AnalysisResultService {

    private final AnalysisResultRepository analysisResultRepository;

    public AnalysisResult create(AnalysisResultDTO analysisResultDTO) {
        AnalysisResult analysisResult = AnalysisResult.toEntity(analysisResultDTO);
        return analysisResultRepository.save(analysisResult);
    }

    public List<AnalysisResult> getByUserId(String userId) {
        return analysisResultRepository.findByUserId(userId);
    }

    public AnalysisResult getLastByUserId(String userId) {
        return analysisResultRepository.findTop1ByUserIdOrderByTimestampDesc(userId);
    }
}
