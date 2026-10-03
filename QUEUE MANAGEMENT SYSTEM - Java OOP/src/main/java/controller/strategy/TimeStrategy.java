package controller.strategy;

import model.Client;
import model.Queue;

import java.util.Collections;
import java.util.Comparator;
import java.util.List;

public class TimeStrategy implements Strategy{
    @Override
    public void addClient(List<Queue> queueList, Client c) {
        queueList.get(0).addClient(c);
        Collections.sort(queueList, new SortByWaitingTime());
    }

    public static class SortByWaitingTime implements Comparator<Queue> {
        @Override
        public int compare(Queue q1, Queue q2) {
            return q1.getWaitTime() - q2.getWaitTime();
        }
    }
}
