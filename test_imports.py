# Test imports
print("Testing imports...")

try:
    from app.db.session import get_db
    print("✓ app.db.session imported successfully")
except Exception as e:
    print(f"✗ Error importing app.db.session: {e}")

try:
    from app.models.superadmin import SuperAdmin
    print("✓ app.models.superadmin imported successfully")
except Exception as e:
    print(f"✗ Error importing app.models.superadmin: {e}")

try:
    from app.core.config import settings
    print("✓ app.core.config imported successfully")
except Exception as e:
    print(f"✗ Error importing app.core.config: {e}")

try:
    from app.core.security import get_password_hash
    print("✓ app.core.security imported successfully")
except Exception as e:
    print(f"✗ Error importing app.core.security: {e}")

print("\nAll core imports tested!")
