package controller.strategy;

import model.Client;
import model.Queue;

import java.util.List;

public interface Strategy {
    public void addClient(List<Queue> queueList, Client c);
}
