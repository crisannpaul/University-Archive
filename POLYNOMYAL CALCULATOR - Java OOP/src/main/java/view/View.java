package view;

import model.Polynome;

import java.awt.*;
import java.awt.event.*;
import javax.swing.*;

public class View extends JFrame {

    private JPanel myPanel;
    private JLabel polynome1L;
    private JLabel polynome2L;
    private JLabel remainderL;
    private JButton addBTN;
    private JButton subBTN;
    private JButton multiplyBTN;
    private JButton divideBTN;
    private JButton integrateBTN;
    private JButton derivateBTN;
    private JLabel quotientL;
    private JTextField polynome1TF;
    private JTextField polynome2TF;

    public View() {
        myPanel = new JPanel();
        polynome1L = new JLabel ("Polynome I:");
        polynome2L = new JLabel ("Polynome II:");
        remainderL = new JLabel ("Remainder:");
        addBTN = new JButton ("+");
        subBTN = new JButton ("-");
        multiplyBTN = new JButton ("x");
        divideBTN = new JButton ("÷");
        integrateBTN = new JButton ("∫P1");
        derivateBTN = new JButton ("P1'");
        quotientL = new JLabel ("Quotient:");
        polynome1TF = new JTextField();
        polynome2TF = new JTextField();

        myPanel.setPreferredSize(new Dimension(944, 599));
        myPanel.setLayout(null);

        myPanel.add(polynome1L);
        myPanel.add(polynome2L);
        myPanel.add(remainderL);
        myPanel.add(addBTN);
        myPanel.add(subBTN);
        myPanel.add(multiplyBTN);
        myPanel.add(divideBTN);
        myPanel.add(integrateBTN);
        myPanel.add(derivateBTN);
        myPanel.add(quotientL);
        myPanel.add(polynome1TF);
        myPanel.add(polynome2TF);

        polynome1L.setFont(polynome1L.getFont().deriveFont(20.0f));
        polynome2L.setFont(polynome2L.getFont().deriveFont(20.0f));
        quotientL.setFont(quotientL.getFont().deriveFont(20.0f));
        remainderL.setFont(remainderL.getFont().deriveFont(20.0f));
        addBTN.setFont(addBTN.getFont().deriveFont(45.0f));
        subBTN.setFont(subBTN.getFont().deriveFont(45.0f));
        multiplyBTN.setFont(multiplyBTN.getFont().deriveFont(45.0f));
        divideBTN.setFont(divideBTN.getFont().deriveFont(45.0f));
        derivateBTN.setFont(derivateBTN.getFont().deriveFont(45.0f));
        integrateBTN.setFont(integrateBTN.getFont().deriveFont(45.0f));
        polynome1TF.setFont(polynome1TF.getFont().deriveFont(21.0f));
        polynome2TF.setFont(polynome2TF.getFont().deriveFont(21.0f));


        polynome1L.setBounds (30, 25, 215, 35);
        polynome2L.setBounds (30, 110, 215, 35);
        remainderL.setBounds (30, 245, 450, 50);
        addBTN.setBounds (30, 300, 75, 75);
        subBTN.setBounds (30, 375, 75, 75);
        multiplyBTN.setBounds (105, 300, 75, 75);
        divideBTN.setBounds (105, 375, 75, 75);
        integrateBTN.setBounds (330, 300, 150, 150);
        derivateBTN.setBounds (180, 300, 150, 150);
        quotientL.setBounds (30, 200, 450, 50);
        polynome1TF.setBounds (30, 60, 450, 50);
        polynome2TF.setBounds (30, 145, 450, 50);

        setTitle(":>");
        setContentPane(myPanel);
        setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);
        pack();
        setVisible(true);
    }

    public String getPolynome1() {
        return polynome1TF.getText();
    }

    public String getPolynome2() {
        return polynome2TF.getText();
    }

    public void setRezult(Polynome q) {
        quotientL.setText("Quotient: " + q.toString());
        remainderL.setText("Remainder: ");
        remainderL.setEnabled(false);
    }
    public void setRezult(Polynome q, Polynome r) {
        quotientL.setText("Quotient: " + q.toString());
        remainderL.setEnabled(true);
        remainderL.setText("Remainder: " + r.toString());
    }

    public void addAdditionListener(ActionListener a) {
        addBTN.addActionListener(a);
    }

    public void addSubstractionListener(ActionListener a) {
        subBTN.addActionListener(a);
    }

    public void addMultiplicationListener(ActionListener a) {
        multiplyBTN.addActionListener(a);
    }

    public void addDivisionListener(ActionListener a) {
        divideBTN.addActionListener(a);
    }

    public void addIntegrationListener(ActionListener a) {
        integrateBTN.addActionListener(a);
    }

    public void addDerivationListener(ActionListener a) {
        derivateBTN.addActionListener(a);
    }

    public void showErr(String errMessage) {
        JOptionPane.showMessageDialog(myPanel, errMessage);
    }

}
