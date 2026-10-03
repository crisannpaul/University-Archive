package disi.savinglives_backend.dtos;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class DoctorDTO {
    private String name;
    private String email;
    private String password;
}
