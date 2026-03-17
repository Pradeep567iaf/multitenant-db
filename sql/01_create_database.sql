-- Multi-Tenant System Database Creation Script
-- Run this first in pgAdmin

-- Create the database
CREATE DATABASE multitenant
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_United States.1252'
    LC_CTYPE = 'English_United States.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Connect to the new database
\c multitenant;

-- Extension for UUID (if needed)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
