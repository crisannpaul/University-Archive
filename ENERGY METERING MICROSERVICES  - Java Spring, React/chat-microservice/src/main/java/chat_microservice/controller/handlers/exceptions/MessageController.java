package chat_microservice.controller.handlers.exceptions;

import chat_microservice.model.ChatMessage;
import chat_microservice.service.MessageService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@CrossOrigin
@RequestMapping("/api/messages")
public class MessageController {

    @Autowired

    private MessageService chatMessageService;

    private final SimpMessagingTemplate simpMessagingTemplate;

    @Autowired
    public MessageController(SimpMessagingTemplate simpMessagingTemplate) {
        this.simpMessagingTemplate = simpMessagingTemplate;
    }

    @MessageMapping("/send-message")
    public void receiveMessage(@Payload ChatMessage chatMessage) {
        System.out.println("Received message: " + chatMessage.getContent());
        if(chatMessage.getType().equals(ChatMessage.MessageType.CHAT)) {
            chatMessage.setTimestamp(LocalDateTime.now());
            chatMessageService.saveMessage(chatMessage);
        }

        if ("admin".equals(chatMessage.getReceiver())) {
            System.out.println("Routing to /topic/admin");
            simpMessagingTemplate.convertAndSend("/topic/admin", chatMessage);
        } else {
            System.out.println("Routing to /topic/users/" + chatMessage.getReceiver());
            simpMessagingTemplate.convertAndSend("/topic/users/" + chatMessage.getReceiver(), chatMessage);
        }

    }

    @GetMapping("/history")
    public ResponseEntity<List<ChatMessage>> getChatHistory(@RequestParam String user1, @RequestParam String user2) {
        System.out.println(user1 + " " + user2);
        List<ChatMessage> messages = chatMessageService.getChatHistory(user1, user2);
        for(ChatMessage msg : messages) {
            System.out.println(msg.toString());
        }
        return ResponseEntity.ok(messages);
    }
}
