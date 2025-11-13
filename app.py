from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nexus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Import and register blueprints
from blueprints.home import home_bp
from blueprints.auth import auth_bp
from blueprints.shop import shop_bp
from blueprints.account import account_bp

app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(shop_bp)
app.register_blueprint(account_bp)

# Run App
if __name__ == "__main__":
    app.run(debug=True)
