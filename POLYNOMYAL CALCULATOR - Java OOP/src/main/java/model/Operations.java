package model;

public abstract class Operations {

    public static Polynome add(Polynome p1, Polynome p2) {
        Polynome rez = p1;
        for(Mononome m : p2.getPolynome()) {
            rez.insertMononome(m);
        }
        return rez;
    }

    public static Polynome substract(Polynome p1, Polynome p2) {
        Polynome rez = p1;
        for(Mononome m : p2.getPolynome()) {
            m.setCoef(m.getCoef() * (-1));
            rez.insertMononome(m);
        }
        return rez;
    }

    public static Polynome multiply(Polynome p1, Polynome p2) {
        Polynome rez = new Polynome();
        for(Mononome m1 : p1.getPolynome()) {
            for(Mononome m2 : p2.getPolynome()) {
                Mononome m = new Mononome(m1.getCoef() * m2.getCoef(), m1.getPow() + m2.getPow());
                rez.insertMononome(m);
            }
        }
        return rez;
    }

    public static Polynome[] divide(Polynome p1, Polynome p2) {
        Polynome dividend = p1;
        Polynome divisor = p2;
        Polynome q = new Polynome();

        while(dividend.getPolynome().get(0).getPow() >= divisor.getPolynome().get(0).getPow()) {
            Mononome x = dividend.getPolynome().get(0);
            Mononome y = divisor.getPolynome().get(0);
            Mononome m = new Mononome(x.getCoef() / y.getCoef(), x.getPow() - y.getPow());
            q.insertMononome(m);

            Polynome temp = new Polynome();
            temp.insertMononome(m);
            temp = multiply(temp, divisor);
            dividend = substract(dividend, temp);
        }

        Polynome[] divisionRez = new Polynome[2];
        divisionRez[0] = q;
        divisionRez[1] = dividend;
        return divisionRez;
    }

    public static Polynome derivate(Polynome p) {
        Polynome rez = new Polynome();
        for(Mononome m : p.getPolynome()) {
            Mononome temp = new Mononome(m.getCoef() * m.getPow(), m.getPow() - 1);
            if(temp.getPow() >= 0) {
                rez.insertMononome(temp);
            }
        }
        return rez;
    }

    public static Polynome integrate(Polynome p) {
        Polynome rez = new Polynome();
        for(Mononome m : p.getPolynome()) {
            Mononome temp = new Mononome(m.getCoef() / (m.getPow() + 1), m.getPow() + 1);
            rez.insertMononome(temp);
        }
        return rez;
    }
}
