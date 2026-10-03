package com.example.liquorstore.dao;

import com.example.liquorstore.entity.Account;
import com.example.liquorstore.entity.Product;
import com.example.liquorstore.form.AccountForm;
import com.example.liquorstore.form.ProductForm;

import org.hibernate.Session;
import org.hibernate.SessionFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;


@Transactional
@Repository
public class AccountDAO {
    @Autowired
    private SessionFactory sessionFactory;
    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    @Transactional(propagation = Propagation.REQUIRES_NEW, rollbackFor = Exception.class)
    public void save(AccountForm newAccount) {

        Session session = this.sessionFactory.getCurrentSession();
        String userName = newAccount.getUserName();

        Account account = null;

        boolean isNew = false;
        if (userName != null) {
            account = this.findAccount(userName);
        }
        if (account == null) {
            isNew = true;
            account = new Account();
            account.setUserRole("ROLE_CUSTOMER");
        }

        account.setUserName(userName);
        account.setEncrytedPassword(passwordEncoder.encode(newAccount.getPassword()));
        account.setActive(true);

        if (isNew) {
            session.persist(account);
        }
        // If error in DB, Exceptions will be thrown out immediately
        session.flush();
    }


    public Account findAccount(String userName) {
        Session session = this.sessionFactory.getCurrentSession();
        return session.find(Account.class, userName);
    }

}
