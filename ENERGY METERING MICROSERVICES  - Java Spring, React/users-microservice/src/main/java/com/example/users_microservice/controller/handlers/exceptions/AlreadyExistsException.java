package com.example.users_microservice.controller.handlers.exceptions;

import org.springframework.http.HttpStatus;

import java.util.ArrayList;

public class AlreadyExistsException extends CustomException{
    private static final String MESSAGE = "Resource already exists!";
    private static final HttpStatus httpStatus = HttpStatus.NOT_ACCEPTABLE;

    public AlreadyExistsException(String resource) {
        super(MESSAGE,httpStatus, resource, new ArrayList<>());
    }
}

