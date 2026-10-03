package disi.savinglives_backend.entities;

import disi.savinglives_backend.dtos.DoctorDTO;
import disi.savinglives_backend.dtos.RegistrationDTO;
import disi.savinglives_backend.entities.enums.BloodGroup;
import disi.savinglives_backend.entities.enums.Role;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.GenericGenerator;

import java.io.Serial;
import java.io.Serializable;
import java.util.UUID;

@Entity
@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class User implements Serializable {
    @Serial
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(generator = "uuid2")
    @GenericGenerator(name = "uuid2", strategy = "uuid2")
    @Column(name="user_id", columnDefinition = "BINARY(16)")
    private UUID id;

    @Column(name = "name", nullable = false)
    private String name;

    @Column(name = "email", nullable = false)
    private String email;

    @Column(name = "password", nullable = false)
    private String password;

    @Enumerated(EnumType.STRING)
    @Column(columnDefinition = "ENUM('ADMIN', 'USER', 'DOCTOR')")
    private Role role;

    @Enumerated(EnumType.STRING)
    @Column(name = "blood_group", columnDefinition = "ENUM('A', 'B', 'AB', 'O')")
    private BloodGroup bloodGroup;

    @Column(name = "weight")
    private Double weight;

    @Column(name = "age")
    private int age;

    @Column(name = "city")
    private String city;

    public static User toEntity(RegistrationDTO registrationDTO) {
        return User.builder()
                .name(registrationDTO.getName())
                .email(registrationDTO.getEmail())
                .password(registrationDTO.getPassword())
                .role(Role.USER)
                .build();
    }

    public static User toEntity(DoctorDTO doctorDTO) {
        return User.builder()
                .name(doctorDTO.getName())
                .email(doctorDTO.getEmail())
                .password(doctorDTO.getPassword())
                .role(Role.DOCTOR)
                .build();
    }
}
