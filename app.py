from flask import Flask
from src.server.models import db
from src.server.routes import register_routes

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smartdispute.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

register_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
