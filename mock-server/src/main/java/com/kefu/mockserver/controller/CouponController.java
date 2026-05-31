package com.kefu.mockserver.controller;

import com.kefu.mockserver.exception.ResourceNotFoundException;
import com.kefu.mockserver.model.Coupon;
import com.kefu.mockserver.repository.CouponRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/coupons")
@CrossOrigin
public class CouponController {

    private final CouponRepository couponRepository;

    public CouponController(CouponRepository couponRepository) {
        this.couponRepository = couponRepository;
    }

    @GetMapping
    public ResponseEntity<List<Coupon>> listCoupons(@RequestParam Integer userId) {
        List<Coupon> coupons = couponRepository.findByUserId(userId);
        return ResponseEntity.ok(coupons);
    }

    @GetMapping("/{code}")
    public ResponseEntity<Coupon> getCouponByCode(@PathVariable String code) {
        Coupon coupon = couponRepository.findByCode(code)
                .orElseThrow(() -> new ResourceNotFoundException("Coupon not found with code: " + code));
        return ResponseEntity.ok(coupon);
    }

    @PostMapping("/use")
    public ResponseEntity<?> useCoupon(@RequestBody Map<String, Object> body) {
        String code = (String) body.get("code");
        Object userIdObj = body.get("userId");

        if (code == null || userIdObj == null) {
            return ResponseEntity.badRequest().body(Map.of("error", "code and userId are required"));
        }

        Integer userId;
        try {
            userId = Integer.valueOf(userIdObj.toString());
        } catch (NumberFormatException e) {
            return ResponseEntity.badRequest().body(Map.of("error", "userId must be an integer"));
        }

        Coupon coupon = couponRepository.findByCode(code)
                .orElseThrow(() -> new ResourceNotFoundException("Coupon not found with code: " + code));

        if (coupon.getUsed()) {
            return ResponseEntity.badRequest().body(Map.of("error", "Coupon already used"));
        }

        if (!coupon.getUserId().equals(userId)) {
            return ResponseEntity.badRequest().body(Map.of("error", "Coupon does not belong to this user"));
        }

        coupon.setUsed(true);
        couponRepository.save(coupon);
        return ResponseEntity.ok(coupon);
    }
}
