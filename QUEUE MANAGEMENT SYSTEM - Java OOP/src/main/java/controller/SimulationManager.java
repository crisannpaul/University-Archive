package controller;
import model.Client;
import view.View;

import java.util.*;

public class SimulationManager implements Runnable{

    private int timeLimit;
    private int[] processingTimeInterval = new int[1];
    private int[] arrivalTimeInterval = new int[1];
    private int nrQueues;
    private int nrClients;
    private SelectionPolicy selectionPolicy;

    private Scheduler scheduler;
    private ArrayList<Client> clientList;
    private Controller controller;
    private View view;

    private double averageWaitingTime;
    private double averageServiceTime;
    private int peakHour;

    public SimulationManager(int timeLimit, int[] arrivalTimeInterval, int[] processingTimeInterval, int nrQueues, int nrClients, SelectionPolicy selectionPolicy, Controller controller, View v) {
            this.timeLimit = timeLimit;
            this.arrivalTimeInterval = arrivalTimeInterval;
            this.processingTimeInterval = processingTimeInterval;
            this.nrQueues = nrQueues;
            this.nrClients = nrClients;
            this.selectionPolicy = selectionPolicy;

            this.scheduler = new Scheduler(nrQueues, selectionPolicy);
            this.clientList = generateClients();
            this.averageServiceTime = calculateAST();
            this.controller = controller;
            this.view = v;
    }

    @Override
    public void run() {
        int currentTime = 0;
        int maxWaitingTime = 0;
        while(currentTime < timeLimit) {
            ArrayList<Client> temp = new ArrayList<Client>();
            for(Client c : clientList) {
                if(c.getAt() == currentTime) {
                    scheduler.assignClient(c);
                    temp.add(c);
                }
            }
            clientList.removeAll(temp);
            currentTime++;

            view.updateView(scheduler.getQueueList(), currentTime, clientListToStringView());
            averageWaitingTime += scheduler.calculateAWT();
            if(scheduler.getCurrentWaitingTime() > maxWaitingTime) {
                peakHour = currentTime;
                maxWaitingTime = scheduler.getCurrentWaitingTime();
            }
            controller.writeInLog(currentTime, clientListToStringLog(), scheduler.toString());
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        averageWaitingTime = averageWaitingTime / timeLimit;
        controller.writeInLog(averageWaitingTime, averageServiceTime, peakHour);
        controller.stopSimulation();
    }

    public ArrayList<Client> generateClients() {
        ArrayList<Client> temp = new ArrayList<Client>();
        for(int i = 0; i < nrClients; i++) {
            Client c = new Client(i, randomNumber(arrivalTimeInterval), randomNumber(processingTimeInterval));
            temp.add(c);
        }
        Collections.sort(temp, new SortClients());
        return temp;
    }

    public int randomNumber(int[] interval) {
        Random random = new Random();
        return (int) ((Math.random() * (interval[1] - interval[0])) + interval[0]);
    }

    public double calculateAST() {
        double serviceTime = 0;
        for (Client c : clientList) {
            serviceTime += c.getSt();
        }
        return serviceTime / clientList.size();
    }

    public String clientListToStringView() {
        String output = "";
        for(Client c : clientList) {
            output += c.toString() + "\n";
        }
        return output;
    }

    public String clientListToStringLog() {
        String output = "";
        for(Client c : clientList) {
            output += c.toString() + " ";
        }
        return output;
    }

    public int getTimeLimit() {
        return timeLimit;
    }

    public void setTimeLimit(int timeLimit) {
        this.timeLimit = timeLimit;
    }

    public int[] getProcessingTimeInterval() {
        return processingTimeInterval;
    }

    public void setProcessingTimeInterval(int[] processingTimeInterval) {
        this.processingTimeInterval = processingTimeInterval;
    }

    public int[] getArrivalTimeInterval() {
        return arrivalTimeInterval;
    }

    public void setArrivalTimeInterval(int[] arrivalTimeInterval) {
        this.arrivalTimeInterval = arrivalTimeInterval;
    }

    public int getNrQueues() {
        return nrQueues;
    }

    public void setNrQueues(int nrQueues) {
        this.nrQueues = nrQueues;
    }

    public int getNrClients() {
        return nrClients;
    }

    public void setNrClients(int nrClients) {
        this.nrClients = nrClients;
    }

    public SelectionPolicy getSelectionPolicy() {
        return selectionPolicy;
    }

    public void setSelectionPolicy(SelectionPolicy selectionPolicy) {
        this.selectionPolicy = selectionPolicy;
    }

    public static class SortClients implements Comparator<Client> {
        @Override
        public int compare(Client c1, Client c2) {
            return c1.getAt() - c2.getAt();
        }
    }
}
