package screenshot;

import net.dv8tion.jda.api.EmbedBuilder;
import net.dv8tion.jda.api.entities.MessageChannel;
import net.dv8tion.jda.api.events.message.MessageReceivedEvent;
import net.dv8tion.jda.api.hooks.ListenerAdapter;
import screenshot.Screenshot;

import java.io.File;
import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;

public class View extends JFrame {

    Screenshot ss = new Screenshot();

    public View() {
        this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        this.setTitle("perspective");
        setSize(500, 400);
        setVisible(true);
    }
}