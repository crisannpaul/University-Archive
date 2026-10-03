package com.example.communication_microservice.config;

import com.example.communication_microservice.compnents.DataMessageBroker;
import com.example.communication_microservice.compnents.DeviceMessageBroker;
import com.example.communication_microservice.service.EnergyDataService;
import com.example.communication_microservice.service.DeviceService;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.rabbit.connection.CachingConnectionFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.listener.MessageListenerContainer;
import org.springframework.amqp.rabbit.listener.SimpleMessageListenerContainer;
import org.springframework.beans.factory.annotation.Value;

@Configuration
public class RabbitMQConfig {

    @Autowired
    private EnergyDataService energyDataService;

    @Autowired
    private DeviceService deviceService;

    @Value("energy_data")
    String dataQueueName;

    @Value("device_sync")
    String deviceQueueName;

    @Value("${spring.rabbitmq.host}")
    String host;

    @Value("${spring.rabbitmq.port}")
    int port;

    @Value("${spring.rabbitmq.username}")
    String username;

    @Value("${spring.rabbitmq.password}")
    String password;

    @Value("${spring.rabbitmq.virtual-host}")
    String virtualHost;

    @Bean
    Queue dataQueue() {
        return new Queue(dataQueueName, false);
    }

    @Bean
    Queue deviceQueue() {
        return new Queue(deviceQueueName, false);
    }

    @Bean
    MessageListenerContainer dataMessageListenerContainer(ConnectionFactory connectionFactory ) {
        SimpleMessageListenerContainer simpleMessageListenerContainer = new SimpleMessageListenerContainer();
        simpleMessageListenerContainer.setConnectionFactory(connectionFactory);
        simpleMessageListenerContainer.setQueues(dataQueue());
        simpleMessageListenerContainer.setMessageListener(new DataMessageBroker(energyDataService));
        return simpleMessageListenerContainer;
    }

    @Bean
    MessageListenerContainer deviceMessageListenerContainer(ConnectionFactory connectionFactory ) {
        SimpleMessageListenerContainer simpleMessageListenerContainer = new SimpleMessageListenerContainer();
        simpleMessageListenerContainer.setConnectionFactory(connectionFactory);
        simpleMessageListenerContainer.setQueues(deviceQueue());
        simpleMessageListenerContainer.setMessageListener(new DeviceMessageBroker(deviceService));
        return simpleMessageListenerContainer;
    }

    @Bean
    public ConnectionFactory connectionFactory() {
        CachingConnectionFactory connectionFactory = new CachingConnectionFactory();
        connectionFactory.setHost(host);
        connectionFactory.setPort(port);
        connectionFactory.setUsername(username);
        connectionFactory.setPassword(password);
        connectionFactory.setVirtualHost(virtualHost);
        return connectionFactory;
    }

    //create MessageListenerContainer using custom connection factory
//	@Bean
//	MessageListenerContainer messageListenerContainer() {
//		SimpleMessageListenerContainer simpleMessageListenerContainer = new SimpleMessageListenerContainer();
//		simpleMessageListenerContainer.setConnectionFactory(connectionFactory());
//		simpleMessageListenerContainer.setQueues(queue());
//		simpleMessageListenerContainer.setMessageListener(new MessageBroker());
//		return simpleMessageListenerContainer;
//
//	}

}
