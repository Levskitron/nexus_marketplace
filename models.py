from datetime import datetime
from database import db

class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False, default="buyer")
    credits_balance = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    shipping_address = db.Column(db.String(200))

    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    account_status = db.Column(db.String(20), default="active")
    last_login = db.Column(db.DateTime)
