import controller.Controller;
import controller.SelectionPolicy;
import controller.SimulationManager;
import view.View;

import java.io.File;
import java.io.IOException;

public class Main {
    public static void main( String[] args ) throws InterruptedException {
        View view = new View();
        Controller controller = new Controller(view);
    }
}


