package com.example.liquorstore.model;

import com.example.liquorstore.entity.Account;

public class AccountInfo {

    private String userName;

    private String password;

    private String repeatPassword;

    public AccountInfo(){}

    public AccountInfo(Account account) {
        this.userName = account.getUserName();
        this.password = account.getEncrytedPassword();
    }

    public AccountInfo(String userName, String password, String repeatPassword) {
        this.userName = userName;
        this.password = password;
        this.repeatPassword = repeatPassword;
    }

    public String getUserName() {
        return userName;
    }

    public void setUserName(String userName) {
        this.userName = userName;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getRepeatPassword() {
        return repeatPassword;
    }

    public void setRepeatPassword(String repeatPassword) {
        this.repeatPassword = repeatPassword;
    }
}
