package perspective;

import commands.AlwaysWatching;
import commands.Death;
import commands.PeekaBoo;
import net.dv8tion.jda.api.AccountType;
import net.dv8tion.jda.api.JDA;
import net.dv8tion.jda.api.JDABuilder;
import net.dv8tion.jda.api.entities.Activity;

import javax.security.auth.login.LoginException;

public class Main {

    public static void main(String[] args) {
        JDABuilder jdaBuilder = JDABuilder.createDefault(System.getenv("DISCORD_TOKEN")).setActivity(Activity.listening("your screams"));
        JDA jda = null;
        jdaBuilder.addEventListeners(new PeekaBoo());
        jdaBuilder.addEventListeners(new Death());
        jdaBuilder.addEventListeners(new AlwaysWatching());
        try {
            jdaBuilder.build();
        } catch (LoginException exception) {
            exception.printStackTrace();
        }

        try {
            jda.awaitReady();
        } catch (InterruptedException exception) {
            exception.printStackTrace();
        }
    }
}