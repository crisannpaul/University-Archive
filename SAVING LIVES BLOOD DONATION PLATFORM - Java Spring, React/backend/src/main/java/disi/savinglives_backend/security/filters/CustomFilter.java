package disi.savinglives_backend.security.filters;

import disi.savinglives_backend.security.JwtUtils;
import io.jsonwebtoken.Claims;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

@RequiredArgsConstructor
public class CustomFilter extends OncePerRequestFilter {

    private final JwtUtils jwtUtils;

    private final String[] AUTH_WHITELIST = { "/api/v1/auth", "/ws" };

    @Override
    protected void doFilterInternal(jakarta.servlet.http.HttpServletRequest request, jakarta.servlet.http.HttpServletResponse response, jakarta.servlet.FilterChain filterChain)
            throws jakarta.servlet.ServletException, IOException {
        // If we are on the WHITELIST we just go forward the filterChain
        for (String path : AUTH_WHITELIST) {
            if (request.getServletPath().startsWith(path)) {
                filterChain.doFilter(request, response);
                return;
            }
        }

        final String requestTokenHeader = request.getHeader(HttpHeaders.AUTHORIZATION);
        Claims claims;
        String token;
        if (requestTokenHeader == null || !requestTokenHeader.startsWith("Bearer ")) {
            response.sendError(400, "NO TOKEN");
            return;
        }
        else {
            token = requestTokenHeader.substring(7);
            try {
                claims = jwtUtils.getBody(token);
            }
            catch (Exception e) {
                response.sendError(401, "Unable to get token");
                return;
            }
        }

        if (claims != null && SecurityContextHolder.getContext().getAuthentication() == null) {
            if (jwtUtils.isValidToken(token)) {
                UsernamePasswordAuthenticationToken usernamePasswordAuthenticationToken = new UsernamePasswordAuthenticationToken(
                        claims.get("user-id"), claims.get("role"), null);
                SecurityContextHolder.getContext().setAuthentication(usernamePasswordAuthenticationToken);
            }
        }
        else {
            response.sendError(403, "Invalid Token");
            return;
        }
        filterChain.doFilter(request, response);
    }
}
