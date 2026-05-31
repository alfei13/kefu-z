package com.kefu.mockserver.repository;

import com.kefu.mockserver.model.Coupon;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface CouponRepository extends JpaRepository<Coupon, Integer> {

    List<Coupon> findByUserId(Integer userId);

    Optional<Coupon> findByCode(String code);
}
