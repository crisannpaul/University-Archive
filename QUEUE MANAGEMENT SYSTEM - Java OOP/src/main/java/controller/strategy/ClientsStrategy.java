package controller.strategy;

import model.Client;
import model.Queue;

import java.util.Collections;
import java.util.Comparator;
import java.util.List;

public class ClientsStrategy implements Strategy{
    @Override
    public void addClient(List<Queue> queueList, Client c) {
        queueList.get(0).addClient(c);
        Collections.sort(queueList, new SortByNrClients());
    }

    public static class SortByNrClients implements Comparator<Queue> {
        @Override
        public int compare(Queue q1, Queue q2) {
            return q1.getNrClients() - q2.getNrClients();
        }
    }
}
