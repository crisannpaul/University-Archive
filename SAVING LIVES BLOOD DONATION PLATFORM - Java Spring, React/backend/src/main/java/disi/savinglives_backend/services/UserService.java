package disi.savinglives_backend.services;

import disi.savinglives_backend.controllers.handlers.exceptions.model.DuplicateResourceException;
import disi.savinglives_backend.controllers.handlers.exceptions.model.ResourceNotFoundException;
import disi.savinglives_backend.dtos.DoctorDTO;
import disi.savinglives_backend.dtos.UserDTO;
import disi.savinglives_backend.dtos.RegistrationDTO;
import disi.savinglives_backend.entities.User;
import disi.savinglives_backend.entities.enums.Role;
import disi.savinglives_backend.repositories.UserRepository;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class UserService {
    private static final Logger LOGGER = LoggerFactory.getLogger(UserService.class);
    private final UserRepository userRepository;

    public User findUserByEmail(String email) {
        Optional<User> user = userRepository.findUserByEmail(email);
        if (!user.isPresent()) {
            LOGGER.error("User with email {} was not found in db", email);
            throw new ResourceNotFoundException(User.class.getSimpleName() + " with email: " + email);
        }

        return user.get();
    }

    public User updateUser(UserDTO userDTO){
        Optional<User> userOptional = userRepository.findById(userDTO.getId());
        if (userOptional.isPresent()){
            User actualUser = userOptional.get();
            // Update email
            if (userDTO.getEmail() != null && !userDTO.getEmail().equals(actualUser.getEmail())) {
                actualUser.setEmail(userDTO.getEmail());
            }
            // Update name
            if (userDTO.getName() != null && !userDTO.getName().equals(actualUser.getName())) {
                actualUser.setName(userDTO.getName());
            }
            // Update password
            if (userDTO.getPassword() != null && !userDTO.getPassword().equals(actualUser.getPassword())) {
                actualUser.setPassword(userDTO.getPassword()); // Consider hashing the password
            }
            // Update role
            if (userDTO.getRole() != null && !userDTO.getRole().equals(actualUser.getRole())) {
                actualUser.setRole(userDTO.getRole());
            }
            // Update blood group
            if (userDTO.getBloodGroup() != null && !userDTO.getBloodGroup().equals(actualUser.getBloodGroup())) {
                actualUser.setBloodGroup(userDTO.getBloodGroup());
            }
            // Update weight
            if (userDTO.getWeight() != null && !userDTO.getWeight().equals(actualUser.getWeight())) {
                actualUser.setWeight(userDTO.getWeight());
            }
            // Update age
            if (userDTO.getAge() != 0 && userDTO.getAge() != actualUser.getAge()) {
                actualUser.setAge(userDTO.getAge());
            }

            // Update city
            if (userDTO.getCity() != null && userDTO.getCity() != actualUser.getCity()) {
                actualUser.setCity(userDTO.getCity());
            }

            userRepository.save(actualUser);
            return actualUser;
        }
        return null;
    }
    public User findUserById(UUID id){
        Optional<User> user = userRepository.findById(id);
        return user.orElse(null);
    }

    public UUID insertUser(RegistrationDTO registrationDTO) {
        User newUser = User.toEntity(registrationDTO);

        if (userRepository.findUserByEmail(newUser.getEmail()).isPresent()){
            LOGGER.error("User with email {} already exists in db", newUser.getEmail());
            throw new DuplicateResourceException(User.class.getSimpleName() + " with email: " + newUser.getEmail());
        }

        newUser = userRepository.save(newUser);
        LOGGER.debug("User with id {} was inserted in db", newUser.getId());
        return newUser.getId();
    }

    public void updatePassword(User user, String newPassword) {
        if (user == null) {
            LOGGER.error("User not found, maybe it's null");
            throw new ResourceNotFoundException(User.class.getSimpleName() + "not found");
        }

        user.setPassword(newPassword);
        userRepository.save(user);
    }

    public List<User> getAllUsers(){
        return userRepository.findAll();
    }

    public User createDoctor(UUID id){
        User user = null;
        Optional<User> maybeUser = userRepository.findById(id);
        if (maybeUser.isPresent()){
            user = maybeUser.get();
            user.setRole(Role.DOCTOR);
            userRepository.save(user);
        }
        return user;
    }


}
