package disi.savinglives_backend.controllers;


import com.google.gson.Gson;
import disi.savinglives_backend.dtos.PasswordResetDTO;
import disi.savinglives_backend.entities.InformativeContent;
import disi.savinglives_backend.services.InformativeContentService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequiredArgsConstructor
@RequestMapping(value = "/api/v1/infoContent")
@CrossOrigin
public class InformativeContentController {

    private final InformativeContentService informativeContentService;

    @GetMapping(value = "/all")
    public ResponseEntity<?> getAllInfoContent() {
        List<InformativeContent> list = informativeContentService.get();
        Gson gson = new Gson();
        String jsonList = gson.toJson(list);
        return ResponseEntity.ok(jsonList);
    }

    @DeleteMapping(value = "/delete/{id}")
    public ResponseEntity<?> deleteId(@PathVariable UUID id) {
        boolean isRemoved = informativeContentService.delete(id);
        if (!isRemoved) {
            return ResponseEntity.status(404).body("InformativeContent with id " + id + " not found");
        }
        return ResponseEntity.ok("InformativeContent with id " + id + " deleted successfully");
    }

    @PostMapping(value = "/create")
    public ResponseEntity<?> createInformativeContent(@RequestBody InformativeContent informativeContent) {
        InformativeContent createdContent = informativeContentService.create(informativeContent);
        return ResponseEntity.ok(createdContent);
    }

}
