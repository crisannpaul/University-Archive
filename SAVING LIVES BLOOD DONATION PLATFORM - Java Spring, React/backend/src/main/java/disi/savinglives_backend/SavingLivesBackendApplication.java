package disi.savinglives_backend;

import disi.savinglives_backend.entities.User;
import disi.savinglives_backend.entities.enums.Role;
import disi.savinglives_backend.repositories.UserRepository;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ConfigurableApplicationContext;

import java.util.UUID;

@SpringBootApplication
public class SavingLivesBackendApplication {

	public static void main(String[] args) {
		ConfigurableApplicationContext context = SpringApplication.run(SavingLivesBackendApplication.class, args);
		UserRepository userRepository = context.getBean(UserRepository.class);

		if (!userRepository.findUserByEmail("admin@admin.com").isPresent()) {
			User admin = User.builder()
					.id(UUID.randomUUID())
					.name("admin")
					.email("admin@admin.com")
					.password("admin")
					.role(Role.ADMIN)
					.build();
			userRepository.save(admin);

		}

		if (!userRepository.findUserByEmail("doctor@doctor.com").isPresent()) {

			User doctor = User.builder()
					.id(UUID.randomUUID())
					.name("doctorotker")
					.email("doctor@doctor.com")
					.password("doctor")
					.role(Role.DOCTOR)
					.build();

			userRepository.save(doctor);
		}
	}
}
