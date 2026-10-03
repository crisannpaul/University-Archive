package com.example.liquorstore.form;

import com.example.liquorstore.model.AccountInfo;


public class AccountForm {

    private String userName;

    private String password;

    private String repeatPassword;

    public AccountForm() {}

    public AccountForm(AccountInfo accountInfo) {
        if(accountInfo != null) {
            this.userName = accountInfo.getUserName();
            this.password = accountInfo.getPassword();
            this.repeatPassword = accountInfo.getRepeatPassword();
        }
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
