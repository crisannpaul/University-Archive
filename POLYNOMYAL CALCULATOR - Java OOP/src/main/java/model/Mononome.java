package model;

public class Mononome {

    private int coef;
    private int pow;

    public Mononome() {
        this.coef = 0;
        this.pow = 0;
    }
    public Mononome(int coef, int pow) {
        this.coef = coef;
        this.pow = pow;
    }

    public String toString() {
        String output = "";
        if(this.coef >= 0) {
            if (this.pow > 0) {
                output += "+" + coef + "X^" + pow + " ";
            } else {
                output += "+" + coef + " ";
            }
        } else {
            if (this.pow > 0) {
                output += coef + "X^" + pow + " ";
            } else {
                output += coef + " ";
            }
        }
        return output;
    }

    public int getCoef() {
        return coef;
    }

    public void setCoef(int coef) {
        this.coef = coef;
    }

    public int getPow() {
        return pow;
    }

    public void setPow(int pow) {
        this.pow = pow;
    }
}
