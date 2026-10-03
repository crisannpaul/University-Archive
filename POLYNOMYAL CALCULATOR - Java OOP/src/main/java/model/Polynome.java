package model;

import java.util.ArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Polynome {
    private ArrayList<Mononome> polynome;

    public Polynome() {
        this.polynome = new ArrayList<Mononome>();
    }

    public Polynome(String input) throws IllegalStateException {
        Pattern pattern = Pattern.compile("([+-]?(?:(?:\\d+x\\^\\d+)|(?:\\d+x)|(?:\\d+)|(?:x)))");
        Matcher matcher = pattern.matcher(input);
        ArrayList<Mononome> polynome = new ArrayList<Mononome>();
        while(matcher.find()) {
            int coef = Integer.parseInt(matcher.group(1));
            matcher.find();
            int pow = Integer.parseInt(matcher.group(1));
            Mononome m = new Mononome(coef, pow);
            polynome.add(m);
        }
        this.polynome = polynome;
    }

    public void insertMononome(Mononome mononome) {
        for (Mononome m : polynome) {
            if (mononome.getPow() == m.getPow()) {
                m.setCoef(m.getCoef() + mononome.getCoef());
                if(m.getCoef() == 0) {
                    polynome.remove(m);
                }
                return;
            }
        }
        polynome.add(mononome);
    }

    public String toString() {
        String output = "";
        for(Mononome m : polynome) {
            output += m.toString();
        }
        return output;
    }

    /*public static void validate(String input) throws InvalidPolynomeException {
        for(int i = 0; i < input.length(); i++) {
            Character x = input.charAt(i);
            Character y = null;
            if (i != input.length() - 1) {
                y = input.charAt(i + 1);
            }
            if(x == 'X' || x == '^' || x == '+' || x == '-' || x == ' ' || Character.isDigit(x)){
                if (x == 'X' && y != '^') {
                    throw new InvalidPolynomeException("ERR");
                }
                if ((x == '+' || x == '-') && !Character.isDigit(y)) {
                    throw new InvalidPolynomeException("ERR");
                }
                if (x == '^' && !Character.isDigit(y)) {
                    throw new InvalidPolynomeException("ERR");
                }
                if (x == ' ' && (y != '+' && y != '-')) {
                    throw new InvalidPolynomeException("ERR");
                }
                if(y != null && (y == '+' || y == '-') && x != ' ') {
                    throw new InvalidPolynomeException("ERR");
                }
            } else {
                throw new InvalidPolynomeException("ERR");
            }
        }
    } */

    public int numberOfTerms(){
        return this.polynome.size();
    }

    public Mononome getTerm(int poz) {
        return this.polynome.get(poz);
    }

    public ArrayList<Mononome> getPolynome() {
        return polynome;
    }

    public void setPolynome(ArrayList<Mononome> polynome) {
        this.polynome = polynome;
    }
}
