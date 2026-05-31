package com.kefu.mockserver.repository;

import com.kefu.mockserver.model.AfterSaleRequest;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface AfterSaleRequestRepository extends JpaRepository<AfterSaleRequest, Integer> {

    List<AfterSaleRequest> findByUserId(Integer userId);

    List<AfterSaleRequest> findByOrderId(Integer orderId);
}
