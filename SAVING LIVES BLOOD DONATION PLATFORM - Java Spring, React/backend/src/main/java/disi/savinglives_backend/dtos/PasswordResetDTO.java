package disi.savinglives_backend.dtos;

import lombok.Data;

@Data
public class PasswordResetDTO extends LoginDTO {
    private String new_password;
}
