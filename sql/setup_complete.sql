-- Multi-Tenant System Complete Setup Script
-- This runs all scripts in order

-- 1. Create Database
\ir 01_create_database.sql

-- 2. Create Tables
\ir 02_create_tables.sql

-- 3. Insert Seed Data
\ir 03_seed_data.sql

-- Setup Complete!
SELECT '=== MULTI-TENANT SYSTEM SETUP COMPLETE ===' AS status;
