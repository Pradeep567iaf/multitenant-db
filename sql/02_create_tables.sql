-- Multi-Tenant System Tables Creation Script
-- Run this after creating the database

-- Connect to multitenant database first
-- \c multitenant;

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS feature_usages CASCADE;
DROP TABLE IF EXISTS billings CASCADE;
DROP TABLE IF EXISTS tenant_users CASCADE;
DROP TABLE IF EXISTS plan_features CASCADE;
DROP TABLE IF EXISTS features CASCADE;
DROP TABLE IF EXISTS plans CASCADE;
DROP TABLE IF EXISTS tenants CASCADE;
DROP TABLE IF EXISTS super_admins CASCADE;

-- Create Super Admins table
CREATE TABLE super_admins (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at VARCHAR(255),
    INDEX email_idx (email)
);

-- Create Plans table
CREATE TABLE plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    created_at VARCHAR(255),
    INDEX name_idx (name)
);

-- Create Features table
CREATE TABLE features (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price_per_use DECIMAL(10,2) NOT NULL,
    INDEX code_idx (code)
);

-- Create Tenants table
CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    plan_id INTEGER REFERENCES plans(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_superadmin_id INTEGER REFERENCES super_admins(id),
    INDEX subdomain_idx (subdomain),
    INDEX email_idx (email)
);

-- Create Tenant Users table
CREATE TABLE tenant_users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(email, tenant_id),
    INDEX tenant_id_idx (tenant_id)
);

-- Create Plan-Features junction table
CREATE TABLE plan_features (
    plan_id INTEGER NOT NULL REFERENCES plans(id) ON DELETE CASCADE,
    feature_id INTEGER NOT NULL REFERENCES features(id) ON DELETE CASCADE,
    PRIMARY KEY (plan_id, feature_id)
);

-- Create Billings table
CREATE TABLE billings (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    total_amount DECIMAL(10,2) NOT NULL,
    billing_period_start DATE NOT NULL,
    billing_period_end DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX tenant_id_idx (tenant_id),
    INDEX billing_period_idx (billing_period_start, billing_period_end)
);

-- Create Feature Usages table
CREATE TABLE feature_usages (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    feature_code VARCHAR(50) NOT NULL,
    usage_count INTEGER NOT NULL DEFAULT 1,
    total_cost DECIMAL(10,2) NOT NULL,
    billing_id INTEGER REFERENCES billings(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX tenant_id_idx (tenant_id),
    INDEX feature_code_idx (feature_code),
    INDEX billing_id_idx (billing_id)
);

-- Add foreign key constraint for tenants.plan_id
ALTER TABLE tenants ADD CONSTRAINT fk_tenant_plan FOREIGN KEY (plan_id) REFERENCES plans(id);
