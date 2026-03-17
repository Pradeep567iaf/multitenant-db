-- Multi-Tenant System Seed Data Script
-- Insert initial plans and features

-- Connect to multitenant database first
-- \c multitenant;

-- Insert Plans
INSERT INTO plans (name, description, created_at) VALUES
('Basic', 'Basic plan with F1 and F2 features', NOW()),
('Advanced', 'Advanced plan with all features (F1, F2, F3, F4)', NOW());

-- Insert Features
INSERT INTO features (code, name, description, price_per_use) VALUES
('F1', 'Feature 1', 'Basic feature 1', 1.00),
('F2', 'Feature 2', 'Basic feature 2', 2.00),
('F3', 'Feature 3', 'Advanced feature 3', 3.00),
('F4', 'Feature 4', 'Advanced feature 4', 4.00);

-- Get plan and feature IDs
-- Basic Plan (ID=1) gets F1, F2
-- Advanced Plan (ID=2) gets F1, F2, F3, F4

-- Insert Plan-Feature associations
INSERT INTO plan_features (plan_id, feature_id) VALUES
(1, 1), -- Basic - F1
(1, 2), -- Basic - F2
(2, 1), -- Advanced - F1
(2, 2), -- Advanced - F2
(2, 3), -- Advanced - F3
(2, 4); -- Advanced - F4

-- Verify data
SELECT 'Plans:' AS section;
SELECT id, name, description FROM plans;

SELECT '' AS blank;

SELECT 'Features:' AS section;
SELECT id, code, name, price_per_use FROM features;

SELECT '' AS blank;

SELECT 'Plan-Feature Associations:' AS section;
SELECT 
    p.name AS plan_name,
    f.code AS feature_code,
    f.name AS feature_name,
    f.price_per_use
FROM plan_features pf
JOIN plans p ON pf.plan_id = p.id
JOIN features f ON pf.feature_id = f.id
ORDER BY p.name, f.code;
