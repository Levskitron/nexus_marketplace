from flask import Flask
from database import db
from blueprints.home import home_bp
from blueprints.auth import auth_bp
from blueprints.shop import shop_bp
from blueprints.account import account_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nexus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialise db with app
db.init_app(app)

# Register blueprints
app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(shop_bp)
app.register_blueprint(account_bp)

# Create tables (including users) once at startup
with app.app_context():
    from models import User  # make sure the model is imported
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
