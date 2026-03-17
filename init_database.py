#!/usr/bin/env python3
"""
Database Initialization Script
Creates database and all required tables for the Multi-Tenant System
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from app.db.session import Base
from app.models import (
    superadmin, tenant, user, plan, feature, 
    plan_feature, billing
)

# Database configuration
DB_USER = "postgres"
DB_PASSWORD = "root"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "multitenant"

# Create database URL for postgres (without specifying database)
POSTGRES_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
# Database URL for the target database
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def create_database():
    """Create the database if it doesn't exist."""
    try:
        # Connect to postgres database to create new database
        engine = create_engine(POSTGRES_URL)
        
        # Check if database exists
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT 1 FROM pg_catalog.pg_database WHERE datname = :dbname"
            ), {"dbname": DB_NAME})
            
            if result.fetchone():
                print(f"Database '{DB_NAME}' already exists.")
                return True
            
            # Create database
            conn.execute(text("COMMIT"))  # Commit any pending transactions
            conn.execute(text(f"CREATE DATABASE {DB_NAME}"))
            print(f"Database '{DB_NAME}' created successfully.")
            return True
            
    except OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
        print("Please check your PostgreSQL credentials and ensure PostgreSQL is running.")
        return False
    except Exception as e:
        print(f"Error creating database: {e}")
        return False


def create_tables():
    """Create all tables using SQLAlchemy models."""
    try:
        # Connect to the target database
        engine = create_engine(DATABASE_URL)
        
        # Create all tables
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("All tables created successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False


def insert_initial_data():
    """Insert initial data (plans and features)."""
    try:
        from sqlalchemy.orm import Session
        from app.db.session import SessionLocal
        from app.models.plan import Plan
        from app.models.feature import Feature
        from app.models.plan_feature import plan_features
        
        db = SessionLocal()
        
        try:
            # Check if data already exists
            if db.query(Plan).count() > 0:
                print("Initial data already exists. Skipping...")
                return True
            
            # Create plans
            print("Inserting initial data...")
            
            basic_plan = Plan(
                name="Basic",
                description="Basic plan with F1 and F2 features"
            )
            advanced_plan = Plan(
                name="Advanced", 
                description="Advanced plan with all features (F1, F2, F3, F4)"
            )
            
            db.add(basic_plan)
            db.add(advanced_plan)
            db.flush()  # Get IDs
            
            # Create features
            f1 = Feature(
                code="F1",
                name="Feature 1",
                description="Basic feature 1",
                price_per_use=1.0
            )
            f2 = Feature(
                code="F2", 
                name="Feature 2",
                description="Basic feature 2",
                price_per_use=2.0
            )
            f3 = Feature(
                code="F3",
                name="Feature 3",
                description="Advanced feature 3",
                price_per_use=3.0
            )
            f4 = Feature(
                code="F4",
                name="Feature 4",
                description="Advanced feature 4",
                price_per_use=4.0
            )
            
            db.add_all([f1, f2, f3, f4])
            db.flush()
            
            # Create plan-feature associations
            # Basic plan: F1, F2
            db.execute(plan_features.insert().values([
                {"plan_id": basic_plan.id, "feature_id": f1.id},
                {"plan_id": basic_plan.id, "feature_id": f2.id},
                # Advanced plan: F1, F2, F3, F4
                {"plan_id": advanced_plan.id, "feature_id": f1.id},
                {"plan_id": advanced_plan.id, "feature_id": f2.id},
                {"plan_id": advanced_plan.id, "feature_id": f3.id},
                {"plan_id": advanced_plan.id, "feature_id": f4.id}
            ]))
            
            db.commit()
            print("Initial data inserted successfully!")
            print("- Plans: Basic, Advanced")
            print("- Features: F1($1), F2($2), F3($3), F4($4)")
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error inserting initial data: {e}")
            return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False


def main():
    """Main execution function."""
    print("=" * 50)
    print("Multi-Tenant System Database Initialization")
    print("=" * 50)
    print()
    
    # Step 1: Create database
    print("[1/3] Creating database...")
    if not create_database():
        sys.exit(1)
    
    print()
    
    # Step 2: Create tables
    print("[2/3] Creating tables...")
    if not create_tables():
        sys.exit(1)
    
    print()
    
    # Step 3: Insert initial data
    print("[3/3] Inserting initial data...")
    if not insert_initial_data():
        print("Warning: Failed to insert initial data. You can do this manually later.")
    
    print()
    print("=" * 50)
    print("✅ Database setup completed successfully!")
    print("=" * 50)
    print()
    print("Database details:")
    print(f"- Name: {DB_NAME}")
    print(f"- Host: {DB_HOST}:{DB_PORT}")
    print(f"- User: {DB_USER}")
    print()
    print("Next steps:")
    print("1. Run the FastAPI server: run_server.bat")
    print("2. Create a superadmin user via API")
    print("3. Start creating tenants!")


if __name__ == "__main__":
    main()
