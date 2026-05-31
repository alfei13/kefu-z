package com.kefu.mockserver.controller;

import com.kefu.mockserver.exception.ResourceNotFoundException;
import com.kefu.mockserver.model.Order;
import com.kefu.mockserver.repository.OrderRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/orders")
@CrossOrigin
public class OrderController {

    private final OrderRepository orderRepository;

    public OrderController(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    @GetMapping
    public ResponseEntity<List<Order>> listOrders(
            @RequestParam(required = false) Integer userId,
            @RequestParam(required = false) String status) {
        if (userId != null && status != null) {
            return ResponseEntity.ok(orderRepository.findByUserIdAndStatus(userId, status));
        } else if (userId != null) {
            return ResponseEntity.ok(orderRepository.findByUserId(userId));
        }
        return ResponseEntity.ok(orderRepository.findAll());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Order> getOrder(@PathVariable Integer id) {
        Order order = orderRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Order not found with id: " + id));
        return ResponseEntity.ok(order);
    }
}
