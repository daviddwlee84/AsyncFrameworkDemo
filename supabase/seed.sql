-- Insert sample test data (optional for demo purposes)
INSERT INTO tasks (type, payload) VALUES 
    ('stripe_create_customer', '{"email": "test@example.com", "name": "Test Customer"}'),
    ('stripe_create_payment', '{"amount": 2000, "currency": "usd", "customer_id": "cus_test123"}')
ON CONFLICT DO NOTHING;