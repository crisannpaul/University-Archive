package com.example.liquorstore.validator;

import com.example.liquorstore.dao.AccountDAO;
import com.example.liquorstore.form.AccountForm;
import com.example.liquorstore.form.ProductForm;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.validation.Errors;
import org.springframework.validation.ValidationUtils;
import org.springframework.validation.Validator;
import org.springframework.validation.annotation.Validated;

@Component
public class AccountFormValidator implements Validator {

    @Autowired
    private AccountDAO accountDAO;

    @Override
    public boolean supports(Class<?> clazz) {
            return clazz == AccountForm.class;
        }

    @Override
    public void validate(Object target, Errors errors) {
        AccountForm accountForm = (AccountForm) target;
        String userName = accountForm.getUserName();
        String password = accountForm.getPassword();
        String repeatPassword = accountForm.getRepeatPassword();

        ValidationUtils.rejectIfEmptyOrWhitespace(errors, "userName", "NotEmpty.accountForm.userName");

        if(password.length() < 3) {
            errors.rejectValue("password", "Password too short");
        }

        if(!password.equals(repeatPassword)) {
            errors.rejectValue("password", "Passwords don't match");
        }

        if(accountDAO.findAccount(userName) != null) {
            errors.rejectValue("userName", "Duplicate.accountForm.userName");
        }
    }
}
