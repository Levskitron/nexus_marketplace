from flask import Flask
from database import db
from models import User   # IMPORTANT

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nexus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "supersecretkey"

db.init_app(app)

with app.app_context():
    db.create_all()

# TEMP test route
@app.route("/")
def home():
    return "Database initialized. Users table created."

if __name__ == "__main__":
    app.run(debug=True)
