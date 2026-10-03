import net.dv8tion.jda.api.AccountType;
import net.dv8tion.jda.api.JDA;
import net.dv8tion.jda.api.JDABuilder;
import net.dv8tion.jda.api.entities.Activity;

import java.security.*;

import javax.security.auth.login.LoginException;

import commands.PeekaBoo;

public class Main {

	public static JDABuilder jda; // java discord app
	
	public static void main(String[] args) throws LoginException{
		JDABuilder jdaBuilder = JDABuilder.createDefault(System.getenv("DISCORD_TOKEN")).setActivity(Activity.listening("your screams"));
		jdaBuilder.addEventListeners(new PeekaBoo());
		JDA jda = null;
		try {
			jdaBuilder.build();
		} catch(LoginException e) {
			e.printStackTrace();
		}
		
		try {
			jda.awaitReady();
		} catch(InterruptedException e) {
			e.printStackTrace();
		}
	}

}
