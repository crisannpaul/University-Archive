package disi.savinglives_backend.controllers;


import disi.savinglives_backend.entities.QRcode;
import disi.savinglives_backend.services.QRcodeService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequiredArgsConstructor
@RequestMapping(value = "/api/v1/qrcode")
@CrossOrigin
public class QRcodeController {
    private final QRcodeService qRcodeService;

    @GetMapping(value = "/get/{id}")
    public ResponseEntity<List<QRcode>> getAllForUser(@PathVariable UUID id) {
        List<QRcode> codes = qRcodeService.getCodesForUser(id.toString());
        return ResponseEntity.ok(codes);
    }
}
