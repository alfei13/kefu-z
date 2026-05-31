package com.kefu.mockserver.repository;

import com.kefu.mockserver.model.Product;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ProductRepository extends JpaRepository<Product, Integer> {

    List<Product> findByCategory(String category);

    List<Product> findByNameContaining(String keyword);
}
