# models.py

from datetime import datetime

from database import db


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Stored as strings (logical enums)
    role = db.Column(db.String(20), nullable=False, default="buyer")  # buyer/seller/admin/super_admin
    shipping_address = db.Column(db.String(200))

    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    account_status = db.Column(db.String(20), default="active")  # active/suspended/deleted
    last_login = db.Column(db.DateTime)

    # Relationships
    products = db.relationship(
        "Product",
        back_populates="seller",
        foreign_keys="Product.seller_id",
        lazy="dynamic",
    )

    orders_as_buyer = db.relationship(
        "Order",
        back_populates="buyer",
        foreign_keys="Order.buyer_id",
        lazy="dynamic",
    )

    orders_as_seller = db.relationship(
        "Order",
        back_populates="seller",
        foreign_keys="Order.seller_id",
        lazy="dynamic",
    )

    reviews = db.relationship(
        "Review",
        back_populates="user",
        lazy="dynamic",
    )

    transactions = db.relationship(
        "Transaction",
        back_populates="user",
        lazy="dynamic",
    )

    support_tickets = db.relationship(
        "SupportTicket",
        back_populates="user",
        lazy="dynamic",
    )

    admin_logs = db.relationship(
        "AdminLog",
        back_populates="admin",
        foreign_keys="AdminLog.admin_id",
        lazy="dynamic",
    )

    admin_logs_as_affected = db.relationship(
        "AdminLog",
        back_populates="affected_user",
        foreign_keys="AdminLog.affected_user_id",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<User {self.user_id} {self.username}>"


class Category(db.Model):
    __tablename__ = "categories"

    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250))

    parent_category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.category_id"),
        nullable=True,
    )

    # Self-referential relationship
    parent_category = db.relationship(
        "Category",
        remote_side=[category_id],
        backref=db.backref("subcategories", lazy="dynamic"),
    )

    products = db.relationship(
        "Product",
        back_populates="category",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<Category {self.category_id} {self.category_name}>"


class Product(db.Model):
    __tablename__ = "products"

    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.category_id"))

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250))
    brand = db.Column(db.String(100))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)

    # Stored as string enums
    condition = db.Column(db.String(20))  # new/used/refurbished
    image_url = db.Column(db.String(255))

    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="active")  # active/inactive/sold_out/removed

    # Relationships
    seller = db.relationship(
        "User",
        back_populates="products",
        foreign_keys=[seller_id],
    )

    category = db.relationship(
        "Category",
        back_populates="products",
    )

    order_items = db.relationship(
        "OrderItem",
        back_populates="product",
        lazy="dynamic",
    )

    reviews = db.relationship(
        "Review",
        back_populates="product",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<Product {self.product_id} {self.name}>"


class Order(db.Model):
    __tablename__ = "orders"

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_status = db.Column(db.String(20), default="pending")  # pending/completed/failed/refunded
    shipping_address = db.Column(db.String(200))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_status = db.Column(db.String(20), default="processing")  # processing/shipped/delivered/cancelled

    # Relationships
    buyer = db.relationship(
        "User",
        back_populates="orders_as_buyer",
        foreign_keys=[buyer_id],
    )

    seller = db.relationship(
        "User",
        back_populates="orders_as_seller",
        foreign_keys=[seller_id],
    )

    items = db.relationship(
        "OrderItem",
        back_populates="order",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    transactions = db.relationship(
        "Transaction",
        back_populates="order",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<Order {self.order_id} buyer={self.buyer_id} seller={self.seller_id}>"


class OrderItem(db.Model):
    __tablename__ = "order_items"

    order_item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)

    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Numeric(10, 2))
    subtotal = db.Column(db.Numeric(10, 2))

    # Relationships
    order = db.relationship(
        "Order",
        back_populates="items",
    )

    product = db.relationship(
        "Product",
        back_populates="order_items",
    )

    def __repr__(self):
        return f"<OrderItem {self.order_item_id} order={self.order_id} product={self.product_id}>"


class Review(db.Model):
    __tablename__ = "reviews"

    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.String(500))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    # NEW: when a user edits an existing review
    edited_at = db.Column(db.DateTime, nullable=True)

    status = db.Column(db.String(20), default="visible")  # visible/hidden/reported

    # Relationships
    product = db.relationship(
        "Product",
        back_populates="reviews",
    )

    user = db.relationship(
        "User",
        back_populates="reviews",
    )

    def __repr__(self):
        return f"<Review {self.review_id} product={self.product_id} user={self.user_id}>"



class Transaction(db.Model):
    __tablename__ = "transactions"

    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    related_order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"))

    transaction_type = db.Column(db.String(20))  # purchase/sale/refund
    amount = db.Column(db.Numeric(10, 2))
    date = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship(
        "User",
        back_populates="transactions",
    )

    order = db.relationship(
        "Order",
        back_populates="transactions",
    )

    def __repr__(self):
        return f"<Transaction {self.transaction_id} user={self.user_id}>"


class StripeCheckoutSession(db.Model):
    __tablename__ = "stripe_checkout_sessions"

    stripe_session_id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

    cart_json = db.Column(db.Text, nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)

    payment_status = db.Column(db.String(20), nullable=False, default="pending")  # pending/paid
    fulfilled = db.Column(db.Boolean, nullable=False, default=False)
    order_ids_json = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User")

    def __repr__(self):
        return f"<StripeCheckoutSession {self.stripe_session_id} user={self.user_id}>"


class SupportTicket(db.Model):
    __tablename__ = "support_tickets"

    ticket_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

    subject = db.Column(db.String(255))
    message = db.Column(db.String(500))
    status = db.Column(db.String(20), default="open")  # open/in_progress/resolved/closed
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)
    admin_response = db.Column(db.String(500))

    # Relationships
    user = db.relationship(
        "User",
        back_populates="support_tickets",
    )

    def __repr__(self):
        return f"<SupportTicket {self.ticket_id} user={self.user_id}>"


class AdminLog(db.Model):
    __tablename__ = "admin_logs"

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    affected_user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))

    action = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    admin = db.relationship(
        "User",
        back_populates="admin_logs",
        foreign_keys=[admin_id],
    )

    affected_user = db.relationship(
        "User",
        back_populates="admin_logs_as_affected",
        foreign_keys=[affected_user_id],
    )

    def __repr__(self):
        return f"<AdminLog {self.log_id} admin={self.admin_id}>"


class ConsultationRequest(db.Model):
    """Stored consultation form submissions."""
    __tablename__ = "consultation_requests"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True)  # optional if not logged in

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30))
    consultation_type = db.Column(db.String(50))  # build_advice, parts_recommendation, troubleshooting, other
    current_setup = db.Column(db.String(500))
    goals_budget = db.Column(db.String(500))
    contact_method = db.Column(db.String(30))  # email, phone, either
    message = db.Column(db.String(1000))
    status = db.Column(db.String(20), default="new")  # new, contacted, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ConsultationRequest {self.id} {self.email}>"


class RepairUpgradeRequest(db.Model):
    """Stored repair/upgrade form submissions."""
    __tablename__ = "repair_upgrade_requests"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True)

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30))
    service_type = db.Column(db.String(30))  # repair, upgrade, both
    device_type = db.Column(db.String(30))  # desktop, laptop, other
    description = db.Column(db.String(1000), nullable=False)
    urgency = db.Column(db.String(50))
    contact_method = db.Column(db.String(30))
    notes = db.Column(db.String(500))
    status = db.Column(db.String(20), default="new")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RepairUpgradeRequest {self.id} {self.email}>"
