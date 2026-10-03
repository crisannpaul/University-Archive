package chat_microservice.repository;

import chat_microservice.model.ChatMessage;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

public interface MessageRepository extends JpaRepository<ChatMessage, Long> {
    List<ChatMessage> findBySenderAndReceiver(String sender, String receiver);

    @Query("select c from ChatMessage c where (c.sender = ?1 and c.receiver = ?2) or (c.sender = ?2 and c.receiver = ?1) order by c.timestamp")
    List<ChatMessage> findBySenderAndReceiverOrderByTimestampAsc(String sender, String receiver);

}
