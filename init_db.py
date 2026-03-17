"""
Database Initialization Script

This script initializes the database with:
1. Default superadmin account
2. Basic and Advanced plans
3. Features (F1, F2, F3, F4)
4. Associates features with plans

Run this after creating the database tables.
"""

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine, Base
from app.models.superadmin import SuperAdmin
from app.models.plan import Plan
from app.models.feature import Feature
from app.models.plan_feature import PlanFeature
from app.core.security import get_password_hash
from datetime import datetime


def init_db():
    """Initialize database with default data."""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 1. Create Superadmin
        print("Creating superadmin account...")
        superadmin_email = "admin@multitenant.com"
        
        existing_superadmin = db.query(SuperAdmin).filter(
            SuperAdmin.email == superadmin_email
        ).first()
        
        if not existing_superadmin:
            superadmin = SuperAdmin(
                email=superadmin_email,
                hashed_password=get_password_hash("admin123"),
                created_at=datetime.utcnow().isoformat()
            )
            db.add(superadmin)
            db.commit()
            print(f"✓ Superadmin created: {superadmin_email} (password: admin123)")
        else:
            print("✓ Superadmin already exists")
        
        # 2. Create Features
        print("\nCreating features...")
        features_data = [
            {"code": "F1", "name": "Feature 1", "cost": 1.0},
            {"code": "F2", "name": "Feature 2", "cost": 2.0},
            {"code": "F3", "name": "Feature 3", "cost": 3.0},
            {"code": "F4", "name": "Feature 4", "cost": 4.0},
        ]
        
        features = {}
        for feature_data in features_data:
            feature = db.query(Feature).filter(
                Feature.code == feature_data["code"]
            ).first()
            
            if not feature:
                feature = Feature(
                    code=feature_data["code"],
                    name=feature_data["name"],
                    cost=feature_data["cost"]
                )
                db.add(feature)
                print(f"✓ Created {feature_data['code']}: {feature_data['name']} (${feature_data['cost']})")
            
            features[feature_data["code"]] = feature
        
        db.commit()
        
        # 3. Create Plans
        print("\nCreating plans...")
        
        # Basic Plan
        basic_plan = db.query(Plan).filter(Plan.name == "Basic").first()
        if not basic_plan:
            basic_plan = Plan(
                name="Basic",
                description="Basic plan with access to F1 and F2 features",
                created_at=datetime.utcnow().isoformat()
            )
            db.add(basic_plan)
            db.commit()
            print("✓ Created Basic plan")
        else:
            print("✓ Basic plan already exists")
        
        # Advanced Plan
        advanced_plan = db.query(Plan).filter(Plan.name == "Advanced").first()
        if not advanced_plan:
            advanced_plan = Plan(
                name="Advanced",
                description="Advanced plan with access to all features (F1, F2, F3, F4)",
                created_at=datetime.utcnow().isoformat()
            )
            db.add(advanced_plan)
            db.commit()
            print("✓ Created Advanced plan")
        else:
            print("✓ Advanced plan already exists")
        
        # 4. Associate Features with Plans
        print("\nAssociating features with plans...")
        
        # Basic Plan: F1, F2
        basic_features = [features["F1"], features["F2"]]
        for feature in basic_features:
            plan_feature = db.query(PlanFeature).filter(
                PlanFeature.plan_id == basic_plan.id,
                PlanFeature.feature_id == feature.id
            ).first()
            
            if not plan_feature:
                plan_feature = PlanFeature(
                    plan_id=basic_plan.id,
                    feature_id=feature.id
                )
                db.add(plan_feature)
                print(f"✓ Added {feature.code} to Basic plan")
        
        # Advanced Plan: F1, F2, F3, F4
        advanced_features = [features["F1"], features["F2"], features["F3"], features["F4"]]
        for feature in advanced_features:
            plan_feature = db.query(PlanFeature).filter(
                PlanFeature.plan_id == advanced_plan.id,
                PlanFeature.feature_id == feature.id
            ).first()
            
            if not plan_feature:
                plan_feature = PlanFeature(
                    plan_id=advanced_plan.id,
                    feature_id=feature.id
                )
                db.add(plan_feature)
                print(f"✓ Added {feature.code} to Advanced plan")
        
        db.commit()
        
        print("\n" + "="*50)
        print("✓ Database initialization completed successfully!")
        print("="*50)
        print("\nDefault Credentials:")
        print(f"  Superadmin Email: {superadmin_email}")
        print(f"  Superadmin Password: admin123")
        print("\nPlans Created:")
        print("  - Basic: F1 ($1), F2 ($2)")
        print("  - Advanced: F1 ($1), F2 ($2), F3 ($3), F4 ($4)")
        print("\nNext Steps:")
        print("  1. Start Celery worker: celery -A celery_worker worker --loglevel=info")
        print("  2. Start FastAPI server: uvicorn app.main:app --reload")
        print("  3. Login as superadmin at http://localhost:8000/docs")
        print("  4. Create tenants and assign plans")
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Error initializing database: {str(e)}")
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    print("="*50)
    print("Multi-Tenant System - Database Initialization")
    print("="*50)
    print("\nThis script will initialize the database with:")
    print("  - 1 Superadmin account")
    print("  - 2 Plans (Basic, Advanced)")
    print("  - 4 Features (F1, F2, F3, F4)")
    print("\nStarting initialization...\n")
    
    init_db()
