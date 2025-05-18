from src.server.extensions import db
from flask_login import UserMixin
from datetime import datetime

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

    cases = db.relationship('Case', backref='user', lazy=True)
    evidence = db.relationship('Evidence', backref='user', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)


class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_paid = db.Column(db.Boolean, default=False)

    # NEW FIELDS FOR AI CLASSIFICATION
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
    payment_type = db.Column(db.String(50))  # e.g., 'legal_package'
    payment_method = db.Column(db.String(50))  # e.g., 'e-transfer', 'paypal'
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
    source_type = db.Column(db.String(50))  # e.g., "canlii", "legislation", "steps-to-justice"
    relevance = db.Column(db.Float)

    def __repr__(self):
        return f"<LegalReference {self.title} from {self.source_type}>"
