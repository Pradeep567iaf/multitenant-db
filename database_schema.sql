-- Multi-Tenant System Database Schema
-- PostgreSQL Database Creation Script

-- Create database (run this separately as superuser)
-- CREATE DATABASE multitenant_db;

-- Connect to the database
-- \c multitenant_db

-- Enable UUID extension (optional, but good practice)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- ============================================================================
-- TABLE: super_admins
-- Description: Stores superadmin accounts
-- ============================================================================
CREATE TABLE super_admins (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for super_admins
CREATE INDEX idx_super_admins_email ON super_admins(email);


-- ============================================================================
-- TABLE: plans
-- Description: Stores subscription plans (Basic, Advanced)
-- ============================================================================
CREATE TABLE plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for plans
CREATE INDEX idx_plans_name ON plans(name);


-- ============================================================================
-- TABLE: features
-- Description: Stores available features (F1, F2, F3, F4)
-- ============================================================================
CREATE TABLE features (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    cost DECIMAL(10, 2) NOT NULL CHECK (cost >= 0)
);

-- Indexes for features
CREATE INDEX idx_features_code ON features(code);


-- ============================================================================
-- TABLE: plan_features
-- Description: Association table between plans and features (many-to-many)
-- ============================================================================
CREATE TABLE plan_features (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL REFERENCES plans(id) ON DELETE CASCADE,
    feature_id INTEGER NOT NULL REFERENCES features(id) ON DELETE CASCADE,
    UNIQUE(plan_id, feature_id)
);

-- Indexes for plan_features
CREATE INDEX idx_plan_features_plan_id ON plan_features(plan_id);
CREATE INDEX idx_plan_features_feature_id ON plan_features(feature_id);


-- ============================================================================
-- TABLE: tenants
-- Description: Stores tenant companies with subdomains
-- ============================================================================
CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    subdomain VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    plan_id INTEGER REFERENCES plans(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_superadmin_id INTEGER REFERENCES super_admins(id) ON DELETE SET NULL
);

-- Indexes for tenants
CREATE INDEX idx_tenants_subdomain ON tenants(subdomain);
CREATE INDEX idx_tenants_email ON tenants(email);
CREATE INDEX idx_tenants_plan_id ON tenants(plan_id);
CREATE INDEX idx_tenants_is_active ON tenants(is_active);


-- ============================================================================
-- TABLE: tenant_users
-- Description: Stores users belonging to tenants
-- ============================================================================
CREATE TABLE tenant_users (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'user')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, email)
);

-- Indexes for tenant_users
CREATE INDEX idx_tenant_users_tenant_id ON tenant_users(tenant_id);
CREATE INDEX idx_tenant_users_email ON tenant_users(email);
CREATE INDEX idx_tenant_users_role ON tenant_users(role);
CREATE INDEX idx_tenant_users_is_active ON tenant_users(is_active);


-- ============================================================================
-- TABLE: billings
-- Description: Stores monthly billing records for tenants
-- ============================================================================
CREATE TABLE billings (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    feature_code VARCHAR(10) NOT NULL,
    usage_count INTEGER DEFAULT 0,
    total_cost DECIMAL(10, 2) DEFAULT 0.00,
    billing_period_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    billing_period_end TIMESTAMP,
    is_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for billings
CREATE INDEX idx_billings_tenant_id ON billings(tenant_id);
CREATE INDEX idx_billings_feature_code ON billings(feature_code);
CREATE INDEX idx_billings_period ON billings(billing_period_start, billing_period_end);
CREATE INDEX idx_billings_is_sent ON billings(is_sent);


-- ============================================================================
-- TABLE: feature_usages
-- Description: Stores individual feature usage records
-- ============================================================================
CREATE TABLE feature_usages (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    feature_code VARCHAR(10) NOT NULL,
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cost DECIMAL(10, 2) NOT NULL
);

-- Indexes for feature_usages
CREATE INDEX idx_feature_usages_tenant_id ON feature_usages(tenant_id);
CREATE INDEX idx_feature_usages_feature_code ON feature_usages(feature_code);
CREATE INDEX idx_feature_usages_used_at ON feature_usages(used_at);


-- ============================================================================
-- INSERT DEFAULT DATA
-- ============================================================================

-- Insert default superadmin (password: admin123)
INSERT INTO super_admins (email, hashed_password, created_at)
VALUES (
    'admin@multitenant.com',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
    CURRENT_TIMESTAMP
) ON CONFLICT (email) DO NOTHING;

-- Insert features
INSERT INTO features (code, name, cost) VALUES
    ('F1', 'Feature 1', 1.00),
    ('F2', 'Feature 2', 2.00),
    ('F3', 'Feature 3', 3.00),
    ('F4', 'Feature 4', 4.00)
ON CONFLICT (code) DO NOTHING;

-- Insert plans
INSERT INTO plans (name, description, created_at) VALUES
    ('Basic', 'Basic plan with access to F1 and F2 features', CURRENT_TIMESTAMP),
    ('Advanced', 'Advanced plan with access to all features (F1, F2, F3, F4)', CURRENT_TIMESTAMP)
ON CONFLICT (name) DO NOTHING;

-- Associate features with Basic plan (F1, F2)
INSERT INTO plan_features (plan_id, feature_id)
SELECT p.id, f.id
FROM plans p, features f
WHERE p.name = 'Basic' AND f.code IN ('F1', 'F2')
ON CONFLICT (plan_id, feature_id) DO NOTHING;

-- Associate features with Advanced plan (F1, F2, F3, F4)
INSERT INTO plan_features (plan_id, feature_id)
SELECT p.id, f.id
FROM plans p, features f
WHERE p.name = 'Advanced' AND f.code IN ('F1', 'F2', 'F3', 'F4')
ON CONFLICT (plan_id, feature_id) DO NOTHING;


-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify tables created
-- SELECT table_name 
-- FROM information_schema.tables 
-- WHERE table_schema = 'public' 
-- ORDER BY table_name;

-- Verify default data
-- SELECT 'Super Admins' as table_name, COUNT(*) as count FROM super_admins
-- UNION ALL
-- SELECT 'Plans', COUNT(*) FROM plans
-- UNION ALL
-- SELECT 'Features', COUNT(*) FROM features
-- UNION ALL
-- SELECT 'Plan Features', COUNT(*) FROM plan_features;


-- ============================================================================
-- USEFUL VIEWS
-- ============================================================================

-- View: Tenant billing summary
CREATE OR REPLACE VIEW tenant_billing_summary AS
SELECT 
    t.id AS tenant_id,
    t.name AS tenant_name,
    t.subdomain,
    t.email AS tenant_email,
    p.name AS plan_name,
    COALESCE(SUM(b.total_cost), 0) AS total_billing,
    COUNT(DISTINCT b.feature_code) AS features_used
FROM tenants t
LEFT JOIN plans p ON t.plan_id = p.id
LEFT JOIN billings b ON t.id = b.tenant_id
GROUP BY t.id, t.name, t.subdomain, t.email, p.name;

-- View: Feature usage statistics
CREATE OR REPLACE VIEW feature_usage_stats AS
SELECT 
    f.code AS feature_code,
    f.name AS feature_name,
    f.cost AS unit_cost,
    COUNT(fu.id) AS total_uses,
    SUM(fu.cost) AS total_revenue
FROM features f
LEFT JOIN feature_usages fu ON f.code = fu.feature_code
GROUP BY f.id, f.code, f.name, f.cost;

-- View: Plan details with features
CREATE OR REPLACE VIEW plan_details AS
SELECT 
    p.id AS plan_id,
    p.name AS plan_name,
    p.description,
    STRING_AGG(f.code || ' - ' || f.name || ' ($' || f.cost || ')', ', ' ORDER BY f.code) AS included_features
FROM plans p
LEFT JOIN plan_features pf ON p.id = pf.plan_id
LEFT JOIN features f ON pf.feature_id = f.id
GROUP BY p.id, p.name, p.description;


-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE super_admins IS 'Stores superadmin accounts for system management';
COMMENT ON TABLE tenants IS 'Stores tenant companies with subdomain-based access';
COMMENT ON TABLE tenant_users IS 'Stores users belonging to different tenants';
COMMENT ON TABLE plans IS 'Stores subscription plans (Basic, Advanced)';
COMMENT ON TABLE features IS 'Stores available features with their costs';
COMMENT ON TABLE plan_features IS 'Many-to-many relationship between plans and features';
COMMENT ON TABLE billings IS 'Stores monthly billing records per tenant per feature';
COMMENT ON TABLE feature_usages IS 'Individual usage records for features';

COMMENT ON COLUMN tenants.subdomain IS 'Subdomain for tenant access (e.g., abc for abc.localhost)';
COMMENT ON COLUMN tenants.plan_id IS 'Current selected plan, NULL until first login';
COMMENT ON COLUMN tenant_users.role IS 'User role: admin or user';
COMMENT ON COLUMN billings.billing_period_start IS 'Start of billing period (usually 1st of month)';
COMMENT ON COLUMN billings.billing_period_end IS 'End of billing period';
COMMENT ON COLUMN billings.is_sent IS 'Whether billing email has been sent';
