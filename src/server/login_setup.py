from src.server.extensions import login_manager
from src.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
