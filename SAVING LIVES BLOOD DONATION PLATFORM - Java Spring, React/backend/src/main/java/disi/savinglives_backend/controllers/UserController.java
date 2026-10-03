package disi.savinglives_backend.controllers;

import disi.savinglives_backend.dtos.DoctorDTO;
import disi.savinglives_backend.dtos.PasswordResetDTO;
import disi.savinglives_backend.dtos.UserDTO;
import disi.savinglives_backend.entities.User;
import disi.savinglives_backend.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.*;
import com.google.gson.Gson;

@RestController
@RequiredArgsConstructor
@RequestMapping(value = "/api/v1/user")
@CrossOrigin
public class UserController {
    private final UserService userService;
  
    @PostMapping(value = "/reset-password")
    public ResponseEntity<?> userPasswordReset(@RequestBody PasswordResetDTO passwordResetDTO) {
        String userId = SecurityContextHolder.getContext().getAuthentication().getPrincipal().toString();
        if (userId == null)
            return new ResponseEntity<>(null, HttpStatus.FORBIDDEN);

        String email = passwordResetDTO.getEmail();
        String password = passwordResetDTO.getPassword();

        User user = userService.findUserByEmail(email);
        if (user == null)
            return new ResponseEntity<>(null, HttpStatus.NOT_FOUND);

        if (!user.getPassword().equals(password))
            return new ResponseEntity<>(null, HttpStatus.NOT_FOUND);

        userService.updatePassword(user, passwordResetDTO.getNew_password());
        return ResponseEntity.ok(null);
    }

    @PostMapping("/update")
    public ResponseEntity<?> updateUser(@RequestBody UserDTO userDTO) {
        User updatedUser = userService.updateUser(userDTO);
        if (updatedUser == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body("User not found.");
        }
        return ResponseEntity.ok(updatedUser);
    }

    @GetMapping("/get")
    public ResponseEntity<?> getUser(@RequestParam UUID userId) {
        User user = userService.findUserById(userId);
        if (user != null) {
            return ResponseEntity.ok(user);
        } else {
            return ResponseEntity.notFound().build();
        }
    }

  @GetMapping("/all")
    public ResponseEntity<?> getAll() {
        List<User> users = userService.getAllUsers();
        Gson gson = new Gson();
        String jsonList = gson.toJson(users);
        return ResponseEntity.ok(jsonList);
    }

    @PutMapping("/create_doctor/{id}")
    public ResponseEntity<?> createDoctor(@PathVariable UUID id){
        User user = userService.createDoctor(id);
        return ResponseEntity.ok(user);
    }
}
