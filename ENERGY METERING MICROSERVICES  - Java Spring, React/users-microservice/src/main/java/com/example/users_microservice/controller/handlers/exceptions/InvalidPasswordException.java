package com.example.users_microservice.controller.handlers.exceptions;

import org.springframework.http.HttpStatus;

import java.util.ArrayList;

public class InvalidPasswordException extends CustomException{

    private static final String MESSAGE = "Invalid password";
    private static final HttpStatus httpStatus = HttpStatus.NOT_ACCEPTABLE;

    public InvalidPasswordException(String resource) {
        super(MESSAGE,httpStatus, resource, new ArrayList<>());
    }
}

