package model;

import java.util.Comparator;

public class Client {
    private int id;
    private int at;
    private int st;

    public Client(int id, int ta, int ts) {
        this.id = id;
        this.at = ta;
        this.st = ts;
    }

    public String toString() {
        return "(" + this.id + ", " + this.at + ", " + this.st + ")";
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public int getAt() {
        return at;
    }

    public void setAt(int ta) {
        this.at = ta;
    }

    public int getSt() {
        return st;
    }

    public void setSt(int st) {
        this.st = st;
    }
}
