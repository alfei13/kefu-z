INSERT INTO product (name, category, price, stock, description, specs, image_url) VALUES
('iPhone 15 Pro', '手机', 8999.00, 50, 'Apple最新旗舰手机，A17 Pro芯片', '屏幕:6.1英寸|处理器:A17 Pro|内存:8GB|存储:256GB', 'https://example.com/iphone15pro.jpg'),
('华为 Mate 60 Pro', '手机', 6999.00, 80, '华为旗舰手机，麒麟9000S芯片', '屏幕:6.8英寸|处理器:麒麟9000S|内存:12GB|存储:512GB', 'https://example.com/mate60pro.jpg'),
('小米14', '手机', 3999.00, 120, '小米旗舰手机，骁龙8 Gen3', '屏幕:6.36英寸|处理器:骁龙8 Gen3|内存:12GB|存储:256GB', 'https://example.com/mi14.jpg'),
('MacBook Pro 14', '笔记本电脑', 14999.00, 30, 'Apple专业笔记本，M3 Pro芯片', '屏幕:14英寸|处理器:M3 Pro|内存:18GB|存储:512GB', 'https://example.com/macbookpro14.jpg'),
('联想 ThinkPad X1 Carbon', '笔记本电脑', 9999.00, 45, '商务旗舰笔记本，轻薄便携', '屏幕:14英寸|处理器:i7-1365U|内存:16GB|存储:512GB', 'https://example.com/x1carbon.jpg'),
('华为 MateBook X Pro', '笔记本电脑', 11999.00, 35, '华为高端轻薄本，3K触控屏', '屏幕:14.2英寸|处理器:i7-1360P|内存:16GB|存储:1TB', 'https://example.com/matebookxpro.jpg'),
('AirPods Pro 2', '耳机', 1899.00, 200, 'Apple主动降噪耳机，自适应通透模式', '类型:入耳式|降噪:主动降噪|连接:蓝牙5.3|续航:6小时', 'https://example.com/airpodspro2.jpg'),
('索尼 WH-1000XM5', '耳机', 2499.00, 150, '索尼旗舰降噪耳机，行业领先降噪', '类型:头戴式|降噪:主动降噪|连接:蓝牙5.2|续航:30小时', 'https://example.com/wh1000xm5.jpg');

INSERT INTO orders (user_id, product_id, product_name, quantity, total_price, status, tracking_no, tracking_company, created_at) VALUES
(1, 1, 'iPhone 15 Pro', 1, 8999.00, 'delivered', 'SF1234567890', '顺丰速运', '2024-01-15 10:30:00'),
(1, 4, 'MacBook Pro 14', 1, 14999.00, 'shipped', 'YT9876543210', '圆通速递', '2024-02-20 14:15:00'),
(1, 7, 'AirPods Pro 2', 2, 3798.00, 'paid', NULL, NULL, '2024-03-10 09:00:00'),
(2, 2, '华为 Mate 60 Pro', 1, 6999.00, 'pending', NULL, NULL, '2024-03-15 16:45:00'),
(2, 8, '索尼 WH-1000XM5', 1, 2499.00, 'cancelled', NULL, NULL, '2024-02-28 11:20:00');

INSERT INTO coupon (code, type, discount_value, min_purchase, valid_until, used, user_id) VALUES
('SAVE100', 'fixed', 100.00, 500.00, '2025-12-31', false, 1),
('OFF20', 'percent', 20.00, 1000.00, '2025-06-30', false, 1),
('WELCOME50', 'fixed', 50.00, 200.00, '2025-12-31', true, 1),
('VIP30', 'percent', 30.00, 2000.00, '2025-09-30', false, 2),
('NEWUSER', 'fixed', 200.00, 1000.00, '2025-12-31', false, 2);

INSERT INTO after_sale_request (order_id, user_id, type, reason, status, created_at) VALUES
(1, 1, 'refund', '手机屏幕有坏点，要求退款', 'pending', '2024-01-20 08:30:00'),
(2, 1, 'exchange', '笔记本键盘有异响，要求换货', 'approved', '2024-02-25 10:00:00'),
(5, 2, 'repair', '耳机降噪功能失效，要求维修', 'rejected', '2024-03-01 14:30:00');
