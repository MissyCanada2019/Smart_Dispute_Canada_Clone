from flask import Flask
from src.server.routes import register_routes  # adjust path if needed
from src.server.models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your.db'  # or your real DB
db.init_app(app)

with app.app_context():
    db.create_all()

register_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
