package com.kefu.mockserver.controller;

import com.kefu.mockserver.exception.ResourceNotFoundException;
import com.kefu.mockserver.model.AfterSaleRequest;
import com.kefu.mockserver.repository.AfterSaleRequestRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/aftersale")
@CrossOrigin
public class AfterSaleController {

    private final AfterSaleRequestRepository afterSaleRequestRepository;

    public AfterSaleController(AfterSaleRequestRepository afterSaleRequestRepository) {
        this.afterSaleRequestRepository = afterSaleRequestRepository;
    }

    @GetMapping
    public ResponseEntity<List<AfterSaleRequest>> listAfterSaleRequests(
            @RequestParam(required = false) Integer userId,
            @RequestParam(required = false) Integer orderId) {
        if (userId != null && orderId != null) {
            List<AfterSaleRequest> byUser = afterSaleRequestRepository.findByUserId(userId);
            List<AfterSaleRequest> byOrder = afterSaleRequestRepository.findByOrderId(orderId);
            byUser.retainAll(byOrder);
            return ResponseEntity.ok(byUser);
        } else if (userId != null) {
            return ResponseEntity.ok(afterSaleRequestRepository.findByUserId(userId));
        } else if (orderId != null) {
            return ResponseEntity.ok(afterSaleRequestRepository.findByOrderId(orderId));
        }
        return ResponseEntity.ok(afterSaleRequestRepository.findAll());
    }

    @PostMapping
    public ResponseEntity<AfterSaleRequest> createAfterSaleRequest(@RequestBody Map<String, Object> body) {
        Object orderIdObj = body.get("orderId");
        Object userIdObj = body.get("userId");
        String type = (String) body.get("type");
        String reason = (String) body.get("reason");

        if (orderIdObj == null || userIdObj == null || type == null || reason == null) {
            return ResponseEntity.badRequest().build();
        }

        Integer orderId;
        Integer userId;
        try {
            orderId = Integer.valueOf(orderIdObj.toString());
            userId = Integer.valueOf(userIdObj.toString());
        } catch (NumberFormatException e) {
            return ResponseEntity.badRequest().build();
        }

        AfterSaleRequest request = new AfterSaleRequest();
        request.setOrderId(orderId);
        request.setUserId(userId);
        request.setType(type);
        request.setReason(reason);
        request.setStatus("pending");
        request.setCreatedAt(LocalDateTime.now());

        AfterSaleRequest saved = afterSaleRequestRepository.save(request);
        return ResponseEntity.ok(saved);
    }

    @PutMapping("/{id}")
    public ResponseEntity<AfterSaleRequest> updateAfterSaleRequest(
            @PathVariable Integer id,
            @RequestBody Map<String, String> body) {
        AfterSaleRequest request = afterSaleRequestRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("After-sale request not found with id: " + id));

        String status = body.get("status");
        if (status != null) {
            request.setStatus(status);
        }

        AfterSaleRequest updated = afterSaleRequestRepository.save(request);
        return ResponseEntity.ok(updated);
    }
}
