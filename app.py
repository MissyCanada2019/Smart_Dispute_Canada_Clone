from flask import Flask, render_template
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Update if you're using a different DB

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Inject current year for Jinja2 templates
@app.context_processor
def inject_now():
    return {'now': datetime.now}

# Import and register routes
from src.server.routes import register_routes
from src.server.admin_routes import register_admin_routes

register_routes(app)
register_admin_routes(app)

# Run the app (only if running locally)
if __name__ == '__main__':
    app.run(debug=True)
