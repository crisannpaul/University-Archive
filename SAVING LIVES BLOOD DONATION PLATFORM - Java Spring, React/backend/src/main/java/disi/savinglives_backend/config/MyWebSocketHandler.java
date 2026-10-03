package disi.savinglives_backend.config;

import disi.savinglives_backend.entities.enums.Role;
import disi.savinglives_backend.services.DonationRequestService;
import disi.savinglives_backend.services.UserService;
import lombok.AllArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;
import disi.savinglives_backend.entities.User;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

@AllArgsConstructor
@Component
public class MyWebSocketHandler extends TextWebSocketHandler {

    private static final Logger logger = LoggerFactory.getLogger(MyWebSocketHandler.class);
    private static ConcurrentHashMap<String, WebSocketSession> sessions = new ConcurrentHashMap<>();

    private final DonationRequestService donationRequestService;
    private final UserService userService;

    @Override
    public void afterConnectionEstablished(WebSocketSession session) throws Exception {
        String userId = session.getUri().getQuery().split("=")[1]; // Assumes query parameter 'id' is used
        sessions.put(userId, session);

        try {
            User user = userService.findUserById(UUID.fromString(userId));

            if (user.getCity() != null && user.getBloodGroup() != null) {
                List<User> matchingUsers = donationRequestService.findAllMatchUsers(user.getCity(), user.getBloodGroup());

                for (User u : matchingUsers) {
                    if (u.equals(user))
                        continue;

                    sendTextMessage(session, u.getName() + " needs you in " + u.getCity());
                    logger.info(u.toString());
                }
            }
        } catch (Exception e) {
            logger.error("Error during connection establishment for user: " + userId, e);
            sendTextMessage(session, "Error during connection establishment.");
            session.close();
        }
    }

    private void sendTextMessage(WebSocketSession session, String message) {
        if (session.isOpen()) {
            try {
                session.sendMessage(new TextMessage(message));
            } catch (IOException e) {
                logger.error("Error sending message: " + message, e);
            }
        } else {
            logger.warn("Attempted to send message to closed session: " + message);
        }
    }

    public void broadcastMessage() throws IOException {
        for (Map.Entry<String, WebSocketSession> entry : sessions.entrySet()) {
            try {
                User user = userService.findUserById(UUID.fromString(entry.getKey()));

                if (user.getRole() != Role.USER) {
                    continue;
                }

                if (user.getCity() != null && user.getBloodGroup() != null) {
                    List<User> matchingUsers = donationRequestService.findAllMatchUsers(user.getCity(), user.getBloodGroup());

                    for (User u : matchingUsers) {
                        if (u.equals(user))
                            continue;

                        sendTextMessage(entry.getValue(), u.getName() + " needs you in " + u.getCity());
                        logger.info(u.toString());
                    }
                }
            } catch (Exception e) {
                logger.error("Error during connection establishment for user: " + entry.getKey(), e);
                sendTextMessage(entry.getValue(), "Error during connection establishment.");
                entry.getValue().close();
            }
        }
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        logger.debug("Received message: " + message.getPayload());
        // Additional message handling logic here
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, org.springframework.web.socket.CloseStatus status) throws Exception {
        String userId = session.getUri().getQuery().split("=")[1];
        sessions.remove(userId);
        logger.debug("Connection closed for user: " + userId + " with status: " + status);
    }
}
