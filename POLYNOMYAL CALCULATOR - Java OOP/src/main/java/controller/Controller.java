package controller;

import model.Polynome;
import view.View;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import static model.Operations.*;

public class Controller {

   Polynome p1;
   Polynome p2;
   Polynome qu;
   Polynome re;
   View v;

   public Controller(View view) {
       v = view;
       p1 = new Polynome();
       p2 = new Polynome();

       v.addAdditionListener(new AdditionListener());
       v.addSubstractionListener(new SubstractionListener());
       v.addMultiplicationListener(new MultiplicationListener());
       v.addDivisionListener(new DivisionListener());
       v.addDerivationListener(new DerivationListener());
       v.addIntegrationListener(new IntegrationListener());
   }

    class AdditionListener implements ActionListener {
        public void actionPerformed(ActionEvent e) {
            try {
                p1 = new Polynome(v.getPolynome1());
                p2 = new Polynome(v.getPolynome2());
                qu = add(p1,p2);
                v.setRezult(qu);
            } catch (IllegalStateException err) {
                v.showErr("Please enter a valid polynome.");
            }
        }
    }

    class SubstractionListener implements ActionListener {
        public void actionPerformed(ActionEvent e) {
            try {
                p1 = new Polynome(v.getPolynome1());
                p2 = new Polynome(v.getPolynome2());
                qu = substract(p1,p2);
                v.setRezult(qu);
            } catch (IllegalStateException err) {
                v.showErr("Please enter a valid polynome.");
            }
        }
    }

    class MultiplicationListener implements ActionListener {
        public void actionPerformed(ActionEvent e) {
            try {
                p1 = new Polynome(v.getPolynome1());
                p2 = new Polynome(v.getPolynome2());
                qu = multiply(p1,p2);
                v.setRezult(qu);
            } catch (IllegalStateException err) {
                v.showErr("Please enter a valid polynome.");
            }
        }
    }

    class DivisionListener implements ActionListener {
        public void actionPerformed(ActionEvent e) {
            try {
                p1 = new Polynome(v.getPolynome1());
                p2 = new Polynome(v.getPolynome2());
                Polynome[] rez = divide(p1,p2);
                qu = rez[0];
                re = rez[1];
                v.setRezult(qu, re);
            } catch (IllegalStateException err) {
                v.showErr("Please enter a valid polynome.");
            }
        }
    }

    class DerivationListener implements ActionListener {
        public void actionPerformed(ActionEvent e) {
            try {
                p1 = new Polynome(v.getPolynome1());
                qu = derivate(p1);
                v.setRezult(qu);
            } catch (IllegalStateException err) {
                v.showErr("Please enter a valid polynome.");
            }
        }
    }

    class IntegrationListener implements ActionListener {
        public void actionPerformed(ActionEvent e) {
            try {
                p1 = new Polynome(v.getPolynome1());
                qu = integrate(p1);
                v.setRezult(qu);
            } catch (IllegalStateException err) {
                v.showErr("Please enter a valid polynome.");
            }
        }
    }
}
