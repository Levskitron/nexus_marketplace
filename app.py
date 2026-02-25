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

# Create tables (including users) once at startup
with app.app_context():
    from models import User  # make sure the model is imported
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
