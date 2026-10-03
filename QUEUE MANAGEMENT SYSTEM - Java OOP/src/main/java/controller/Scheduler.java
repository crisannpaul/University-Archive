package controller;

import controller.strategy.ClientsStrategy;
import controller.strategy.Strategy;
import controller.strategy.TimeStrategy;
import model.Client;
import model.Queue;

import java.util.ArrayList;

public class Scheduler {

    private ArrayList<Queue> queueList;
    private Strategy strategy;

    public Scheduler(int maxQueues, SelectionPolicy policy) {
        queueList = new ArrayList<Queue>();
        for(int i = 0; i < maxQueues; i++) {
            Queue q = new Queue();
            Thread t = new Thread(q);
            t.start();
            this.queueList.add(q);
        }
        changeSelectionPolicy(policy);
    }

    public void changeSelectionPolicy(SelectionPolicy policy) {
        if(policy == SelectionPolicy.SHORTEST_QUEUE) {
            this.strategy = new ClientsStrategy();
        } else if(policy == SelectionPolicy.SHORTEST_TIME) {
            this.strategy = new TimeStrategy();
        }
    }

    public void assignClient(Client c) {
        strategy.addClient(this.queueList, c);
    }

    public double calculateAWT() {
        int waitingTime = 0;
        for(Queue q : queueList) {
            waitingTime += q.getWaitTime();
        }
        if(queueList.size() != 0) {
            return waitingTime / queueList.size();
        }
        else {
            return 0;
        }
    }

    public int getCurrentWaitingTime() {
        int waitingTime = 0;
        for(Queue q : queueList) {
            waitingTime += q.getWaitTime();
        }
        return waitingTime;
    }

    public ArrayList<Queue> getQueueList() {
        return this.queueList;
    }

    public String toString() {
        String output = "";
        int index = 1;
        for(Queue q : queueList) {
            output += "Queue " + index + ": ";
            for(Client c : q.getQueue()) {
                output += c.toString() + " ";
            }
            output += "\n";
            index++;
        }
        return output;
    }
}
