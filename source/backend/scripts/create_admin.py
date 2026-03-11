"""
Script to create the first admin user in MongoDB.

Usage:
    python -m backend.scripts.create_admin
"""

from __future__ import annotations

import asyncio
import getpass

from backend.database.mongodb import Mongo
from backend.utils.security import hash_password


async def create_admin() -> None:
    """Create an admin user interactively."""
    Mongo.connect()
    db = Mongo.db
    if db is None:
        raise RuntimeError("Database not connected")

    print("Create Admin User")
    print("=" * 40)
    
    name = input("Admin name: ").strip()
    if not name:
        print("Name is required")
        return

    email = input("Email: ").strip()
    if not email:
        print("Email is required")
        return

    phone_number = input("Phone number: ").strip()
    if not phone_number or len(phone_number) < 10:
        print("Valid phone number (at least 10 digits) is required")
        return

    # Check if admin already exists
    existing = await db["admin"].find_one({"email": email})
    if existing:
        print(f"Admin with email {email} already exists")
        return

    password = getpass.getpass("Password: ")
    if len(password) < 6:
        print("Password must be at least 6 characters")
        return

    password_confirm = getpass.getpass("Confirm password: ")
    if password != password_confirm:
        print("Passwords do not match")
        return

    # Create admin
    admin_doc = {
        "name": name,
        "email": email,
        "phone_number": phone_number,
        "password_hash": hash_password(password),
        "role": "admin",
    }

    await db["admin"].insert_one(admin_doc)
    print(f"\nAdmin user '{name}' ({email}) created successfully!")
    print("You can now login at POST /auth/login")


if __name__ == "__main__":
    asyncio.run(create_admin())
    Mongo.close()
