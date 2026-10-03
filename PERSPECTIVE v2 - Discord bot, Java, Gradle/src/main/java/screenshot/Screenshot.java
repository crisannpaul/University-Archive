package screenshot;

import com.sun.javafx.font.directwrite.RECT;

import javax.imageio.ImageIO;
import javax.swing.*;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Random;

public class Screenshot {

    private File imageFile = null;

    public Screenshot() {
        Random rand = new Random();
        Robot robot = null;
        try {
            robot = new Robot();
        } catch (AWTException e) {
            e.printStackTrace();
        }
        robot.delay(1 * 60000);
        Dimension d = new Dimension(Toolkit.getDefaultToolkit().getScreenSize());
        int width = (int) d.getWidth();
        int height = (int) d.getHeight();
        BufferedImage capture = robot.createScreenCapture(new Rectangle(0, 0, width, height));
        imageFile = new File("screenshot" + rand.nextInt(99999) +".jpg");
        try {
            ImageIO.write(capture, "jpg", imageFile);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public String getScreenshotPath() {
        return this.imageFile.getAbsolutePath();
    }

    public String getScreenshotName() {
        return this.imageFile.getName();
    }
    public void deleteFile() {
        try {
            Files.deleteIfExists(Paths.get(imageFile.getAbsolutePath()));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
