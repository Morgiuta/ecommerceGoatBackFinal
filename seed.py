#!/usr/bin/env python3
"""
Seed script to populate the database with initial data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import get_db_session
from models.client import ClientModel
from services.client_service import ClientService
from schemas.client_schema import ClientSchema

def create_admin_user():
    """Create an admin user if it doesn't exist."""
    session = get_db_session()
    try:
        # Check if admin user already exists
        admin_user = session.query(ClientModel).filter(ClientModel.email == "admin@techstore.com").first()
        if admin_user:
            print("Admin user already exists.")
            return

        # Create admin user
        admin_data = ClientSchema(
            name="Admin",
            lastname="TechStore",
            email="admin@techstore.com",
            telephone="+549123456789",
            password="admin123",  # In production, this should be hashed
            is_admin=True
        )

        client_service = ClientService()
        admin_user = client_service.create(admin_data)
        print(f"Admin user created: {admin_user.email}")

    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    create_admin_user()
