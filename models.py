from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    subscription_type = db.Column(db.String(20), default="free")  # free, pay_per_doc, unlimited, low_income
    subscription_end = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    cases = db.relationship('Case', backref='user', lazy=True)
    documents = db.relationship('Document', backref='user', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # landlord-tenant, credit, human-rights, etc.
    status = db.Column(db.String(20), default="in_progress")  # in_progress, completed
    merit_score = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = db.relationship('Document', backref='case', lazy=True)
    generated_forms = db.relationship('GeneratedForm', backref='case', lazy=True)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # pdf, image, docx, etc.
    extracted_text = db.Column(db.Text, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Document metadata (renamed to doc_metadata to avoid conflicts with SQLAlchemy)
    doc_metadata = db.Column(db.JSON, nullable=True)  # Extracted metadata from document

class GeneratedForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    form_type = db.Column(db.String(50), nullable=False)  # LTB-T6, credit-dispute, etc.
    form_data = db.Column(db.JSON, nullable=False)  # Form fields and values
    generated_file_path = db.Column(db.String(512), nullable=True)
    is_paid = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Citations and legal references used
    citations = db.Column(db.JSON, nullable=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)  # per_document, subscription
    payment_method = db.Column(db.String(20), nullable=False)  # paypal, stripe
    payment_id = db.Column(db.String(100), nullable=False)  # External payment ID
    status = db.Column(db.String(20), nullable=False)  # completed, pending, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # If document payment, reference to the document
    generated_form_id = db.Column(db.Integer, db.ForeignKey('generated_form.id'), nullable=True)

class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='session', lazy=True)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    is_user = db.Column(db.Boolean, default=True)  # True if from user, False if from AI
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class LegalIssue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # landlord-tenant, credit, human-rights, etc.
    issue_type = db.Column(db.String(100), nullable=False)  # mold, eviction, credit-report-error, etc.
    description = db.Column(db.Text, nullable=False)
    applicable_laws = db.Column(db.JSON, nullable=False)  # Laws and statutes that apply
    required_forms = db.Column(db.JSON, nullable=False)  # Forms needed for this issue
    
    # Related issues
    related_issues = db.relationship(
        'LegalIssue',
        secondary='related_issues',
        primaryjoin='LegalIssue.id==related_issues.c.issue_id',
        secondaryjoin='LegalIssue.id==related_issues.c.related_issue_id',
        backref='related_to'
    )

# Association table for related legal issues
related_issues = db.Table('related_issues',
    db.Column('issue_id', db.Integer, db.ForeignKey('legal_issue.id'), primary_key=True),
    db.Column('related_issue_id', db.Integer, db.ForeignKey('legal_issue.id'), primary_key=True)
)
