#!/usr/bin/env python3
"""
Simple test script to check what's causing the crash
"""

import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_environment():
    """Test environment variables"""
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY_SUPERADMIN', 
        'SECRET_KEY_TENANT'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        else:
            logger.info(f"✓ {var}: {'*' * 10}")  # Hide actual values
    
    if missing:
        logger.error(f"❌ Missing environment variables: {missing}")
        return False
    
    logger.info("✓ All required environment variables present")
    return True

def test_imports():
    """Test if all modules can be imported"""
    try:
        logger.info("Testing imports...")
        from app.db.session import engine
        logger.info("✓ Database session imported")
        
        from app.core.config import settings
        logger.info("✓ Config imported")
        
        from app.models.superadmin import SuperAdmin
        logger.info("✓ Models imported")
        
        return True
    except Exception as e:
        logger.error(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database connection"""
    try:
        logger.info("Testing database connection...")
        from app.db.session import engine
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            logger.info("✓ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("=== Starting Deployment Diagnostics ===")
    
    # Test 1: Environment
    if not test_environment():
        exit(1)
    
    # Test 2: Imports
    if not test_imports():
        exit(1)
    
    # Test 3: Database
    if not test_database():
        exit(1)
    
    logger.info("✅ All tests passed! Application should start successfully.")
