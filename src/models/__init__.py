from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from src.server.extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    postal_code = db.Column(db.String(20))
    province = db.Column(db.String(5))
    subscription_type = db.Column(db.String(50), default="free")
    subscription_end = db.Column(db.DateTime, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(50), default="user")

    cases = db.relationship('Case', backref='user', lazy=True)
    evidence = db.relationship('Evidence', backref='user', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self):
        from itsdangerous import URLSafeTimedSerializer
        from flask import current_app
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps(self.email, salt='email-confirm')

    @staticmethod
    def verify_confirmation_token(token, expiration=3600):
        from itsdangerous import URLSafeTimedSerializer
        from flask import current_app
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            email = serializer.loads(token, salt='email-confirm', max_age=expiration)
        except Exception:
            return None
        return email

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_paid = db.Column(db.Boolean, default=False)

    legal_issue = db.Column(db.String(100))
    matched_keywords = db.Column(db.Text)
    confidence_score = db.Column(db.Float)

    evidence = db.relationship('Evidence', backref='case', lazy=True)
    payments = db.relationship('Payment', backref='case', lazy=True)
    legal_references = db.relationship('LegalReference', backref='case', lazy=True)

class Evidence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    tag = db.Column(db.String(100))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False, default=5.99)
    payment_type = db.Column(db.String(50))
    payment_method = db.Column(db.String(50))
    payment_id = db.Column(db.String(150), nullable=True)
    status = db.Column(db.String(50), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LegalReference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    title = db.Column(db.String(255))
    url = db.Column(db.String(512))
    snippet = db.Column(db.Text)
    citation = db.Column(db.String(255))
    court = db.Column(db.String(255))
    date = db.Column(db.String(64))
    source_type = db.Column(db.String(50))
    relevance = db.Column(db.Float)

    def __repr__(self):
        return f"<LegalReference {self.title} from {self.source_type}>"

class FormTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    court = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))
    url = db.Column(db.String(500), nullable=False)
    jurisdiction = db.Column(db.String(50), default="ontario")
    file_type = db.Column(db.String(20), default="doc")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from datetime import datetime

from src.server.extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    postal_code = db.Column(db.String(20))
    province = db.Column(db.String(5))
    subscription_type = db.Column(db.String(50), default="free")
    subscription_end = db.Column(db.DateTime, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(50), default="user")

    cases = db.relationship('Case', backref='user', lazy=True)
    evidence = db.relationship('Evidence', backref='user', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self):
        from itsdangerous import URLSafeTimedSerializer
        from flask import current_app
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps(self.email, salt='email-confirm')

    @staticmethod
    def verify_confirmation_token(token, expiration=3600):
        from itsdangerous import URLSafeTimedSerializer
        from flask import current_app
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            email = serializer.loads(token, salt='email-confirm', max_age=expiration)
        except Exception:
            return None
        return email

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_paid = db.Column(db.Boolean, default=False)

    legal_issue = db.Column(db.String(100))
    matched_keywords = db.Column(db.Text)
    confidence_score = db.Column(db.Float)

    evidence = db.relationship('Evidence', backref='case', lazy=True)
    payments = db.relationship('Payment', backref='case', lazy=True)

class Evidence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    tag = db.Column(db.String(100))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False, default=5.99)
    payment_type = db.Column(db.String(50))
    payment_method = db.Column(db.String(50))
    payment_id = db.Column(db.String(150), nullable=True)
    status = db.Column(db.String(50), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LegalReference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    title = db.Column(db.String(255))
    url = db.Column(db.String(512))
    snippet = db.Column(db.Text)
    citation = db.Column(db.String(255))
    court = db.Column(db.String(255))
    date = db.Column(db.String(64))
    source_type = db.Column(db.String(50))
    relevance = db.Column(db.Float)

    def __repr__(self):
        return f"<LegalReference {self.title} from {self.source_type}>"

class FormTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    court = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))
    url = db.Column(db.String(500), nullable=False)
    jurisdiction = db.Column(db.String(50), default="ontario")
    file_type = db.Column(db.String(20), default="doc")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
