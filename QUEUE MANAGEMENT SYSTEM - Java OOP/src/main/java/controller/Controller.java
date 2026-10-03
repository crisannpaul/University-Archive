package controller;

import view.View;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

public class Controller {

    private View view;
    private Thread mainThread;
    private File log;

    public Controller(View v) {
        view = v;

        v.addSimulateListener(new SimulateListener());
    }

    public void stopSimulation() {
        mainThread.interrupt();
    }

    class SimulateListener implements ActionListener {
        public void actionPerformed(ActionEvent e) {
            int timeLimit = view.getTimeLimit();
            int[] arrivalTimeInterval = view.getAtInterval();
            int[] serviceTimeInteval = view.getStInterval();
            int nrQueues = view.getNrQueues();
            int nrClients = view.getNrClients();
            SelectionPolicy selectionPolicy = view.getSelectionPolicy();
            mainThread = new Thread(new SimulationManager(timeLimit, arrivalTimeInterval, serviceTimeInteval, nrQueues, nrClients, selectionPolicy, Controller.this, view));
            createLog();
            mainThread.start();
        }
    }

    /**
     *
     */
    public void createLog() {
        try {
            log = new File("EventLog.txt");
            if (log.createNewFile()) {
                System.out.println("File created: " + log.getName());
            } else {
                System.out.println("File already exists.");
            }
        } catch (IOException e) {
            System.out.println("An error occurred.");
            e.printStackTrace();
        }
    }

    public void writeInLog(int currentTime, String clientList, String queues) {
        try {
            FileWriter myWriter = new FileWriter("EventLog.txt", true);
            myWriter.append("Time: " + currentTime + "\n");
            myWriter.append("Clients: " + clientList);
            myWriter.append("\n");
            myWriter.append(queues);
            myWriter.append("\n");
            myWriter.close();
        } catch (IOException e) {
            System.out.println("An error occurred.");
            e.printStackTrace();
        }
    }

    public void writeInLog(double averageWaitingTime, double averageServiceTime, int peakHour) {
        try {
            FileWriter myWriter = new FileWriter("EventLog.txt", true);
            myWriter.append("Average waiting time: " + averageWaitingTime + "\n");
            myWriter.append("Average service time: " + averageServiceTime + "\n");
            myWriter.append("Peak hour: " + peakHour);
            myWriter.close();
        } catch (IOException e) {
            System.out.println("An error occurred.");
            e.printStackTrace();
        }
    }
}

