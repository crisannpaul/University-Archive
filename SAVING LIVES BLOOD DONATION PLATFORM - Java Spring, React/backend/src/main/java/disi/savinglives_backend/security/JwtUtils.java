package disi.savinglives_backend.security;

import disi.savinglives_backend.dtos.AuthDTO;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import org.springframework.stereotype.Component;

import java.sql.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;

@Component
public class JwtUtils {
    private final SignatureAlgorithm signatureAlgorithm = SignatureAlgorithm.HS512;
    private final String secret_key = System.getenv().getOrDefault("JWT_SECRET", "change-me-change-me-change-me-change-me-change-me-change-me-change-me");

    public String generateToken(AuthDTO subject) {
        return Jwts.builder()
                .setSubject(subject.getId())
                .setClaims(new HashMap(Map.of("user-id", subject.getId(), "role", subject.getRole())))
                .setIssuedAt(new Date(System.currentTimeMillis()))
                .setExpiration(new Date(System.currentTimeMillis() + TimeUnit.HOURS.toMillis(1)))
                .signWith(signatureAlgorithm, secret_key.getBytes()).compact();
    }

    public boolean isValidToken(String token) {
        return !isTokenExpired(token);
    }

    // code to get body
    public Claims getBody(String token) {
        return Jwts.parser().setSigningKey(secret_key.getBytes()).parseClaimsJws(token).getBody();
    }

    // code to get subject
    public String getSubject(String token) {
        return getBody(token).getSubject();
    }

    // code to check if token is expired
    public boolean isTokenExpired(String token) {
        return getBody(token).getExpiration().before(new Date(System.currentTimeMillis()));
    }
}
