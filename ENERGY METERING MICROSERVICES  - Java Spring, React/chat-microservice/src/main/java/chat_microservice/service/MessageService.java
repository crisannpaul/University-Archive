package chat_microservice.service;

import chat_microservice.model.ChatMessage;
import chat_microservice.repository.MessageRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class MessageService {

    private final MessageRepository chatMessageRepository;

    public MessageService(MessageRepository chatMessageRepository) {
        this.chatMessageRepository = chatMessageRepository;
    }

    public void saveMessage(ChatMessage chatMessage) {
        // Additional logic can be added here if needed
        chatMessageRepository.save(chatMessage);
    }

    public List<ChatMessage> getChatHistory(String sender, String receiver) {
        // Implement the logic to fetch chat history from the repository
        // This method might vary based on how you've defined it in your repository
        return chatMessageRepository.findBySenderAndReceiverOrderByTimestampAsc(sender, receiver);
    }

}
