package com.example.em_microservice.config;

import com.rabbitmq.client.ConnectionFactory;
import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitMQConfig {

    @Value("device_sync")
    private String queue;

//    @Value("device_sync")
    private String exchange;

//    @Value("device_sync")
    private String routingKey;

    // spring bean for rabbitmq queue
    @Bean
    public Queue queue() {
        return new Queue(queue, false);
    }

    // spring bean for rabbitmq exchange
//    @Bean
//    public TopicExchange exchange() {
//        return new TopicExchange(exchange);
//    }
//
//    // binding between queue and exchange using routing key
//    @Bean
//    public Binding binding() {
//        return BindingBuilder
//                .bind(queue())
//                .to(exchange())
//                .with(routingKey);
//    }


//    @Bean
//    public MessageConverter converter() {
//        return new Jackson2JsonMessageConverter();
//    }
}

