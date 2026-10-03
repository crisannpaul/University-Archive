package disi.savinglives_backend.dtos;

import lombok.Builder;
import lombok.Data;

@Data
public class RegistrationDTO {
    private String name;
    private String email;
    private String password;
}
