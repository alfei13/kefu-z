package com.kefu.mockserver.repository;

import com.kefu.mockserver.model.Order;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface OrderRepository extends JpaRepository<Order, Integer> {

    List<Order> findByUserId(Integer userId);

    List<Order> findByUserIdAndStatus(Integer userId, String status);
}
