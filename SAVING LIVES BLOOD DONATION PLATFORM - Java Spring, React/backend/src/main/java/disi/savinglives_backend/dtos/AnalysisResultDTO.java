package disi.savinglives_backend.dtos;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class AnalysisResultDTO {
    private String userId;
    private String analysisDescription;
    private String eligibility;
}
