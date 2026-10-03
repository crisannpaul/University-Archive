import model.Mononome;
import model.Polynome;
import org.junit.*;

import static model.Operations.*;
import static org.junit.Assert.assertEquals;


public class OperationsTest {
    Polynome p1;
    Polynome p2;
    
    @Before
    public void setUp() {
        p1 = new Polynome("2X^3 +3X^2 -1X^1 +5X^0");
        p2 = new Polynome("1X^2 -1X^1 +1X^0");
    }

    @Test
    public void testAddition() {
        Polynome rez = add(p1, p2);
        System.out.println("(2X^3 +3X^2 -1X^1 +5X^0) + (1X^2 -1X^1 +1X^0) should equal to (2x^3 +4X^2 −2x^1 +6X^0)");

        assertEquals("First element's coefficient = 2", 2, rez.getTerm(0).getCoef());
        assertEquals("First element's exponent = 3", 3, rez.getTerm(0).getPow());
        assertEquals("Second element's coefficient = 4", 4, rez.getTerm(1).getCoef());
        assertEquals("Second element's exponent = 2", 2, rez.getTerm(1).getPow());
        assertEquals("Third element's coefficient = -2", -2, rez.getTerm(2).getCoef());
        assertEquals("Third element's exponent = 1", 1, rez.getTerm(2).getPow());
        assertEquals("Fourth element's coefficient = 6", 6, rez.getTerm(3).getCoef());
        assertEquals("Fourtn element's exponent = 0", 0, rez.getTerm(3).getPow());

        System.out.println("It actually does!");
    }

    @Test
    public void testSubstraction() {
        Polynome rez = substract(p1, p2);
        System.out.println("(2X^3 +3X^2 -1X^1 +5X^0) - (1X^2 -1X^1 +1X^0) should equal to (2x^3 +3X^2 +4X^0)");

        assertEquals("First element's coefficient = 2", 2, rez.getTerm(0).getCoef());
        assertEquals("First element's exponent = 3", 3, rez.getTerm(0).getPow());
        assertEquals("Second element's coefficient = 2", 2, rez.getTerm(1).getCoef());
        assertEquals("Second element's exponent = 2", 2, rez.getTerm(1).getPow());
        assertEquals("Third element's coefficient = 4", 4, rez.getTerm(2).getCoef());
        assertEquals("Third element's exponent = 0", 0, rez.getTerm(2).getPow());

        System.out.println("It actually does!");
    }

    @Test
    public void testMultiplication() {
        Polynome rez = multiply(p1, p2);
        System.out.println("(2X^3 +3X^2 -1X^1 +5X^0) x (1X^2 -1X^1 +1X^0) should equal to (2x^5 +1X^4 -2X^3 +9X^2 -6X^1 +5X^0)");

        assertEquals("First element's coefficient = 2", 2, rez.getTerm(0).getCoef());
        assertEquals("First element's exponent = 5", 5, rez.getTerm(0).getPow());
        assertEquals("Second element's coefficient = 1", 1, rez.getTerm(1).getCoef());
        assertEquals("Second element's exponent = 4", 4, rez.getTerm(1).getPow());
        assertEquals("Third element's coefficient = -2", -2, rez.getTerm(2).getCoef());
        assertEquals("Third element's exponent = 3", 3, rez.getTerm(2).getPow());
        assertEquals("Fourth element's coefficient = 9", 9, rez.getTerm(3).getCoef());
        assertEquals("Fourtn element's exponent = 2", 2, rez.getTerm(3).getPow());
        assertEquals("Fifth element's coefficient = -6", -6, rez.getTerm(4).getCoef());
        assertEquals("Fifth element's exponent = 1", 1, rez.getTerm(4).getPow());
        assertEquals("Sixth element's coefficient = 5", 5, rez.getTerm(5).getCoef());
        assertEquals("Sixth element's exponent = 0", 0, rez.getTerm(5).getPow());

        System.out.println("It actually does!");
    }

    @Test
    public void testDivision() {
        Polynome[] rez = divide(p1, p2);
        Polynome q = rez[0];
        Polynome r= rez[1];
        System.out.println("(2X^3 +3X^2 -1X^1 +5X^0) x (1X^2 -1X^1 +1X^0) should equal to: Q: (2x^1 +5X^0), R: (2X^1)");

        assertEquals("Quotient's first element's coefficient = 2", 2, q.getTerm(0).getCoef());
        assertEquals("Quotient's first element's exponent = 1", 1, q.getTerm(0).getPow());
        assertEquals("Quotient's second element's coefficient = 5", 5, q.getTerm(1).getCoef());
        assertEquals("Quotient's second element's exponent = 0", 0, q.getTerm(1).getPow());

        assertEquals("Remainder's first element's coefficient = 2", 2, r.getTerm(0).getCoef());
        assertEquals("Remainder's first element's exponent = 1", 1, r.getTerm(0).getPow());

        System.out.println("It actually does!");
    }
}
