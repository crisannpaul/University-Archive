package model;

import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;

public class Queue implements Runnable {

    private BlockingQueue<Client> queue;
    private int waitTime;

    public Queue() {
        queue = new ArrayBlockingQueue<Client>(100);
        this.waitTime = 0;
    }

    @Override
    public void run() {
        while(true) {
            if (!queue.isEmpty()) {
                try {
                    int serviceTime = queue.peek().getSt();
                    for (int i = 0; i < serviceTime; i++) {
                        Thread.sleep(1000);
                        if(this.waitTime > 0) {
                            this.waitTime--;
                        }
                    }
                    queue.take();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    public void addClient(Client c) {
        queue.add(c);
        this.waitTime += c.getSt();
    }

    public int getNrClients() {
        return queue.size();
    }

    public String toString() {
        String output = "";
        for(int i = 0; i < queue.size(); i++) {
            output += "(I) ";
        }
        return output;
    }

    public BlockingQueue<Client> getQueue() {
        return queue;
    }

    public void setQueue(BlockingQueue<Client> queue) {
        this.queue = queue;
    }

    public int getWaitTime() {
        return waitTime;
    }

    public void setWaitTime(int waitTime) {
        this.waitTime = waitTime;
    }
}

