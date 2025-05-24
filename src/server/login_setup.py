# src/server/login_setup.py
from src.models import User

def load_user(user_id):
    return User.query.get(int(user_id))
