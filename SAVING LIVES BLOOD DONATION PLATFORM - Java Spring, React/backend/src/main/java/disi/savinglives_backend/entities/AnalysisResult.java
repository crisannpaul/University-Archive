package disi.savinglives_backend.entities;


import disi.savinglives_backend.dtos.AnalysisResultDTO;
import disi.savinglives_backend.dtos.RegistrationDTO;
import disi.savinglives_backend.entities.enums.Role;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.GenericGenerator;

import java.io.Serial;
import java.util.Date;
import java.util.UUID;

@Entity
@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class AnalysisResult {

    @Serial
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(generator = "uuid2")
    @GenericGenerator(name = "uuid2", strategy = "uuid2")
    @Column(name="id", columnDefinition = "BINARY(16)")
    private UUID id;

    @Column(name = "user_id", nullable = false)
    private String userId;

    @Column(name = "analysis_description")
    private String analysisDescription;

    @Column(name = "eligibility")
    private String eligibility;

    @Column(name = "timestamp")
    private Date timestamp;

    public static AnalysisResult toEntity(AnalysisResultDTO analysisResultDTO) {
        return AnalysisResult.builder()
                .userId(analysisResultDTO.getUserId())
                .analysisDescription(analysisResultDTO.getAnalysisDescription())
                .eligibility(analysisResultDTO.getEligibility())
                .timestamp(new Date())
                .build();
    }
}
