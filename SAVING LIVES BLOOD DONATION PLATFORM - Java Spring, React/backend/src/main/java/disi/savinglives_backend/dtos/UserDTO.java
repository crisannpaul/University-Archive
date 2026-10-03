package disi.savinglives_backend.dtos;

import disi.savinglives_backend.entities.enums.BloodGroup;
import disi.savinglives_backend.entities.enums.Role;
import lombok.Data;

import java.util.UUID;

@Data
public class UserDTO {

    private UUID id;
    private String name;
    private String email;
    private String password;
    private Role role;
    private BloodGroup bloodGroup;
    private Double weight;
    private int age;
    private String city;


    public UserDTO(UUID id, String name, String email, String password, Role role) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.password = password;
        this.role = role;
    }

    public UserDTO(UUID id){
        this.id = id;
    }
    public UserDTO() {
    }
}
