from flask import Flask, session
from database import db
from blueprints.home import home_bp
from blueprints.auth import auth_bp
from blueprints.shop import shop_bp
from blueprints.account import account_bp
from blueprints.seller import seller_bp
from blueprints.admin import admin_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Make user available in ALL templates
@app.context_processor
def inject_user():
    from models import User  # local import to avoid circular import
    user = None

    if session.get("user_id"):
        user = User.query.get(session["user_id"])

    return dict(user=user)


# SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nexus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["UPLOAD_FOLDER"] = "static/images/products"

# Initialise db with app
db.init_app(app)

# Register blueprints
app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(shop_bp)
app.register_blueprint(account_bp)
app.register_blueprint(seller_bp)
app.register_blueprint(admin_bp)

# Create tables and ensure categories exist (so /shop/category/... works on fresh deploy e.g. Render)
def ensure_categories():
    from models import Category
    categories = [
        ("PC Parts", None),
        ("CPU", "PC Parts"),
        ("GPU", "PC Parts"),
        ("Motherboard", "PC Parts"),
        ("RAM", "PC Parts"),
        ("Storage", "PC Parts"),
        ("Power Supplies", "PC Parts"),
        ("Games & Accessories", None),
        ("Games", "Games & Accessories"),
        ("Accessories", "Games & Accessories"),
        ("Services", None),
        ("Consultation", "Services"),
        ("Prebuilt", "Services"),
        ("Repair & Upgrade", "Services"),
    ]

    def get_category(name):
        return Category.query.filter_by(category_name=name).first()

    for name, parent_name in categories:
        parent = get_category(parent_name) if parent_name else None
        if get_category(name):
            continue
        new_cat = Category(
            category_name=name,
            parent_category_id=parent.category_id if parent else None,
        )
        db.session.add(new_cat)
    db.session.commit()

with app.app_context():
    from models import User  # make sure the model is imported
    db.create_all()
    ensure_categories()

if __name__ == "__main__":
    app.run(debug=True)
