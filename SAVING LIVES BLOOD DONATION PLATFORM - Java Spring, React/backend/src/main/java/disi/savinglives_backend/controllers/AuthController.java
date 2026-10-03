package disi.savinglives_backend.controllers;

import disi.savinglives_backend.controllers.handlers.exceptions.model.DuplicateResourceException;
import disi.savinglives_backend.dtos.AuthDTO;
import disi.savinglives_backend.dtos.LoginDTO;
import disi.savinglives_backend.dtos.RegistrationDTO;
import disi.savinglives_backend.entities.User;
import disi.savinglives_backend.security.JwtUtils;
import disi.savinglives_backend.services.DonationRequestService;
import disi.savinglives_backend.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping(value = "/api/v1/auth")
@RequiredArgsConstructor
@CrossOrigin
public class AuthController {
    private final UserService userService;
    private final JwtUtils jwtUtils;
    private final DonationRequestService donationRequestService;

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginDTO loginDTO) {
        String email = loginDTO.getEmail();
        String password = loginDTO.getPassword();

        User user = userService.findUserByEmail(email);
        if (user == null)
            return new ResponseEntity<>(null, HttpStatus.NOT_FOUND);

        if (!user.getPassword().equals(password))
            return new ResponseEntity<>(null, HttpStatus.NOT_FOUND);

        Map<String, String> jsonResponse = new HashMap<>();
        jsonResponse.put("id", String.valueOf(user.getId()));
        jsonResponse.put("role", String.valueOf(user.getRole()));
        jsonResponse.put("bloodGroup", String.valueOf(user.getBloodGroup()));
        jsonResponse.put("weight", String.valueOf(user.getWeight()));
        jsonResponse.put("age", String.valueOf(user.getAge()));

        AuthDTO authDTO = new AuthDTO(user.getId().toString(), user.getRole().toString());
        String token = jwtUtils.generateToken(authDTO);
        jsonResponse.put("token", token);



        return ResponseEntity.ok(jsonResponse);
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody RegistrationDTO registrationDTO) {
        try {
            UUID userUuid = userService.insertUser(registrationDTO);
            return new ResponseEntity<>(userUuid, HttpStatus.CREATED);
        } catch (DuplicateResourceException e) {
            return ResponseEntity
                    .status(HttpStatus.CONFLICT)
                    .body("Registration failed: " + e.getMessage());
        } catch (Exception e) {
            return ResponseEntity
                    .status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("An error occurred during registration.");
        }
    }
}
