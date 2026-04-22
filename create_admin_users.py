"""
One-off script to create admin and superadmin accounts.
Run from the project root:  python create_admin_users.py
"""
from werkzeug.security import generate_password_hash

from app import app
from database import db
from models import User


PASSWORD = "Password"


def main():
    with app.app_context():
        # Ensure tables exist
        db.create_all()

        for username, role, email in [
            ("admin", "admin", "admin@nexus.local"),
            ("superadmin", "super_admin", "superadmin@nexus.local"),
        ]:
            existing = User.query.filter_by(username=username).first()
            if existing:
                existing.role = role
                existing.password_hash = generate_password_hash(PASSWORD)
                existing.account_status = "active"
                db.session.add(existing)
                print(f"Updated user '{username}' to role={role}, password reset.")
            else:
                user = User(
                    username=username,
                    email=email,
                    password_hash=generate_password_hash(PASSWORD),
                    role=role,
                    account_status="active",
                )
                db.session.add(user)
                print(f"Created user '{username}' with role={role}.")

        db.session.commit()
        print("Done. You can sign in with username 'admin' or 'superadmin' and password 'Password'.")


if __name__ == "__main__":
    main()
