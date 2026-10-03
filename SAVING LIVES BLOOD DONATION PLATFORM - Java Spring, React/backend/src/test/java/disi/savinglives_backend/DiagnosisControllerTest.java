package disi.savinglives_backend;

import disi.savinglives_backend.dtos.AuthDTO;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.*;

import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import disi.savinglives_backend.security.JwtUtils;
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class DiagnosisControllerTest {

    @LocalServerPort
    private int port;

    @Autowired
    private TestRestTemplate restTemplate;

    @Autowired
    private JwtUtils jwtUtils;

    @Test
    public void testGetDiagnosis() {
        String url = "http://localhost:8080/api/diagnosis/get";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        AuthDTO authDTO = new AuthDTO("69", "ADMIN");
        String token = jwtUtils.generateToken(authDTO);
        headers.setBearerAuth(token);

        String symptoms = "Cough, Fever";

        HttpEntity<String> entity = new HttpEntity<>(symptoms, headers);

        ResponseEntity<Map> response = restTemplate.exchange(url, HttpMethod.POST, entity, Map.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).containsKey("diagnosis");
    }

    @Test
    public void testGetDiagnosisServiceUnavailable() {
        // Assuming the Flask service is not running or will return an error
        String url = "http://localhost:" + port + "/api/diagnosis/get";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        String symptoms = "Cough, Fever";

        HttpEntity<String> entity = new HttpEntity<>(symptoms, headers);

        ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.POST, entity, String.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
    }
}