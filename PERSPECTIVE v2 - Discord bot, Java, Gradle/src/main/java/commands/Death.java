package commands;

import net.dv8tion.jda.api.EmbedBuilder;
import net.dv8tion.jda.api.MessageBuilder;
import net.dv8tion.jda.api.entities.MessageChannel;
import net.dv8tion.jda.api.events.message.MessageReceivedEvent;
import net.dv8tion.jda.api.hooks.ListenerAdapter;

import java.io.File;
import java.io.FileNotFoundException;

public class Death extends ListenerAdapter {

    @Override
    public void onMessageReceived(MessageReceivedEvent event)
    {
        MessageChannel channel = event.getChannel();
        if(event.getMessage().getContentRaw().equalsIgnoreCase("hi perspective")) {
            channel.sendMessage("hello")
                    .addFile(new File("death.jpg"))
                    .setEmbeds(new EmbedBuilder()
                            .setImage("attachment://death.jpg")
                            .build())
                    .queue(); // this actually sends the information to discor
        }
    }
}
