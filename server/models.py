from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    postal_code = db.Column(db.String(10))
    province = db.Column(db.String(50))
    date_of_birth = db.Column(db.String(20))

class GeneratedForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    form_name = db.Column(db.String(100))
    file_path = db.Column(db.String(200))
    is_paid = db.Column(db.Boolean, default=False)
