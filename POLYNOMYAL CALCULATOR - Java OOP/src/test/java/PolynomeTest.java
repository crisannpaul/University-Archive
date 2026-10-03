import model.Mononome;
import model.Polynome;
import org.junit.*;

import static org.junit.Assert.assertEquals;


public class PolynomeTest {

    Polynome p;

    @Before
    public void setUp()
    {
        p = new Polynome();
    }

    @Test
    public void testPolynome()
    {
        assertEquals("a new Polynome should have no terms", 0, p.getPolynome().size());
    }

    public void testinsertTerm() {
        p.insertMononome(new Mononome(3, 2));
        assertEquals("3x^2 was added",             1,   p.numberOfTerms());
        assertEquals("coefficient was set to 3.0", 3, p.getTerm(0).getCoef());
        assertEquals("exponent was set to 2",      2,   p.getTerm(0).getPow());
        p.insertMononome(new Mononome(-3, 1));
        assertEquals("-3x was added",                2,   p.numberOfTerms());
        assertEquals("coefficient was set to -3.0", -3, p.getTerm(1).getCoef());
        assertEquals("exponent was set to 1",        1,   p.getTerm(1).getPow());
    }

    @Test
    public void testConstructor() {
        p = new Polynome("2X^3 +3X^2 -1X^1 +5X^0");
        assertEquals("First element's coefficient = 2", 2, p.getTerm(0).getCoef());
        assertEquals("First element's exponent = 3", 3, p.getTerm(0).getPow());
        assertEquals("Second element's coefficient = 3", 3, p.getTerm(1).getCoef());
        assertEquals("Second element's exponent = 2", 2, p.getTerm(1).getPow());
        assertEquals("Third element's coefficient = -1", -1, p.getTerm(2).getCoef());
        assertEquals("Third element's exponent = 1", 1, p.getTerm(2).getPow());
        assertEquals("Fourth element's coefficient = 5", 5, p.getTerm(3).getCoef());
        assertEquals("Fourtn element's exponent = 0", 0, p.getTerm(3).getPow());
    }

}
