import os
import uuid
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import (
    render_template, request, redirect, url_for, flash, 
    session, jsonify, send_file, abort
)
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from models import User, Case, Document, GeneratedForm, Payment, ChatSession, ChatMessage
from utils.ocr import process_document
from utils.legal_analyzer import analyze_case, get_merit_score, get_recommended_forms
from utils.document_generator import generate_legal_document
from utils.canlii_api import search_canlii, get_relevant_precedents
from utils.payment import process_paypal_payment
from utils.ai_chat import generate_ai_response

def init_routes(app):
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}
    
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    @app.route('/')
    def index():
        return render_template('index.html')
        
    @app.route('/about')
    def about():
        return render_template('about.html')
        
    @app.route('/legal-disclaimer')
    def legal_disclaimer():
        return render_template('legal_disclaimer.html')
        
    @app.route('/privacy-policy')
    def privacy_policy():
        return render_template('privacy_policy.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
            
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            else:
                flash('Invalid email or password', 'danger')
                
        return render_template('login.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
            # Check if user already exists
            existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
            if existing_user:
                flash('Username or email already exists', 'danger')
                return render_template('register.html')
                
            # Create new user
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
            
        return render_template('register.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        user_cases = Case.query.filter_by(user_id=current_user.id).order_by(Case.updated_at.desc()).all()
        return render_template('dashboard.html', cases=user_cases)
    
    @app.route('/upload', methods=['GET', 'POST'])
    @login_required
    def upload():
        if request.method == 'POST':
            # Check if case title exists
            case_title = request.form.get('case_title')
            case_category = request.form.get('case_category')
            
            if not case_title or not case_category:
                flash('Please provide a case title and select a category', 'danger')
                return redirect(url_for('upload'))
                
            # Create a new case
            new_case = Case(
                user_id=current_user.id,
                title=case_title,
                category=case_category
            )
            db.session.add(new_case)
            db.session.commit()
            
            # Check if files were uploaded
            if 'files[]' not in request.files:
                flash('No files selected', 'danger')
                return redirect(url_for('upload'))
                
            files = request.files.getlist('files[]')
            
            # Process each file
            for file in files:
                if file and allowed_file(file.filename):
                    # Create unique filename
                    original_filename = secure_filename(file.filename)
                    file_extension = original_filename.rsplit('.', 1)[1].lower()
                    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                    
                    # Create user directory if it doesn't exist
                    user_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id))
                    os.makedirs(user_dir, exist_ok=True)
                    
                    # Save file
                    file_path = os.path.join(user_dir, unique_filename)
                    file.save(file_path)
                    
                    # Process document with OCR
                    extracted_text, metadata = process_document(file_path, file_extension)
                    
                    # Save document info to database
                    new_document = Document(
                        user_id=current_user.id,
                        case_id=new_case.id,
                        filename=original_filename,
                        file_path=file_path,
                        file_type=file_extension,
                        extracted_text=extracted_text,
                        doc_metadata=metadata
                    )
                    db.session.add(new_document)
            
            db.session.commit()
            return redirect(url_for('analyze', case_id=new_case.id))
            
        return render_template('upload.html')
    
    @app.route('/analyze/<int:case_id>')
    @login_required
    def analyze(case_id):
        case = Case.query.get_or_404(case_id)
        
        # Check if user owns the case
        if case.user_id != current_user.id:
            abort(403)
            
        # Get documents for this case
        documents = Document.query.filter_by(case_id=case.id).all()
        
        # If no documents, redirect to upload
        if not documents:
            flash('Please upload documents first', 'warning')
            return redirect(url_for('upload'))
            
        # Analyze case
        analysis = analyze_case(case, documents)
        
        # Update case with merit score
        merit_score = get_merit_score(analysis)
        case.merit_score = merit_score
        db.session.commit()
        
        # Get relevant precedents
        precedents = get_relevant_precedents(case.category, analysis)
        
        # Get recommended forms
        recommended_forms = get_recommended_forms(case.category, analysis)
        
        return render_template(
            'analyze.html', 
            case=case, 
            documents=documents, 
            analysis=analysis,
            merit_score=merit_score,
            precedents=precedents,
            recommended_forms=recommended_forms
        )
    
    @app.route('/generate/<int:case_id>', methods=['GET', 'POST'])
    @login_required
    def generate(case_id):
        case = Case.query.get_or_404(case_id)
        
        # Check if user owns the case
        if case.user_id != current_user.id:
            abort(403)
            
        if request.method == 'POST':
            form_type = request.form.get('form_type')
            if not form_type:
                flash('Please select a form type', 'danger')
                return redirect(url_for('generate', case_id=case.id))
                
            # Get form data from request
            form_data = {}
            for key, value in request.form.items():
                if key != 'form_type' and key != 'csrf_token':
                    form_data[key] = value
                    
            # Generate legal document
            try:
                documents = Document.query.filter_by(case_id=case.id).all()
                file_path, citations = generate_legal_document(
                    case, 
                    documents, 
                    form_type, 
                    form_data
                )
                
                # Save generated form
                new_form = GeneratedForm(
                    case_id=case.id,
                    form_type=form_type,
                    form_data=form_data,
                    generated_file_path=file_path,
                    citations=citations
                )
                db.session.add(new_form)
                db.session.commit()
                
                return redirect(url_for('preview', form_id=new_form.id))
                
            except Exception as e:
                logging.error(f"Error generating document: {str(e)}")
                flash('Error generating document. Please try again.', 'danger')
                return redirect(url_for('generate', case_id=case.id))
        
        # Get recommended forms for this case
        documents = Document.query.filter_by(case_id=case.id).all()
        analysis = analyze_case(case, documents)
        recommended_forms = get_recommended_forms(case.category, analysis)
        
        return render_template('generate.html', case=case, recommended_forms=recommended_forms)
    
    @app.route('/preview/<int:form_id>')
    @login_required
    def preview(form_id):
        form = GeneratedForm.query.get_or_404(form_id)
        case = Case.query.get_or_404(form.case_id)
        
        # Check if user owns the case
        if case.user_id != current_user.id:
            abort(403)
            
        # Check if subscription allows downloading without watermark
        can_download_clean = current_user.subscription_type != "free"
        
        return render_template('preview.html', form=form, case=case, can_download_clean=can_download_clean)
    
    @app.route('/download/<int:form_id>/<string:version>')
    @login_required
    def download(form_id, version):
        form = GeneratedForm.query.get_or_404(form_id)
        case = Case.query.get_or_404(form.case_id)
        
        # Check if user owns the case
        if case.user_id != current_user.id:
            abort(403)
            
        # Check if user has permission to download clean version
        if version == 'clean' and current_user.subscription_type == 'free':
            flash('Please upgrade your subscription to download clean documents', 'warning')
            return redirect(url_for('pricing'))
            
        # If pay-per-document, check if paid
        if version == 'clean' and current_user.subscription_type == 'pay_per_doc' and not form.is_paid:
            return redirect(url_for('pay_document', form_id=form.id))
            
        # Get the file path based on version
        file_path = form.generated_file_path
        
        # For clean version, remove watermark if needed
        if version == 'clean' and not os.path.exists(file_path.replace('.pdf', '_clean.pdf')):
            # Logic to remove watermark would go here
            pass
            
        return send_file(file_path, as_attachment=True)
    
    @app.route('/pay_document/<int:form_id>', methods=['GET', 'POST'])
    @login_required
    def pay_document(form_id):
        form = GeneratedForm.query.get_or_404(form_id)
        case = Case.query.get_or_404(form.case_id)
        
        # Check if user owns the case
        if case.user_id != current_user.id:
            abort(403)
            
        if request.method == 'POST':
            payment_method = request.form.get('payment_method')
            if payment_method == 'paypal':
                paypal_payment_id = request.form.get('paypal_payment_id')
                if paypal_payment_id:
                    # Process PayPal payment
                    payment_status = process_paypal_payment(paypal_payment_id, 5.99)
                    
                    if payment_status == 'completed':
                        # Mark document as paid
                        form.is_paid = True
                        
                        # Record payment
                        payment = Payment(
                            user_id=current_user.id,
                            amount=5.99,
                            payment_type='per_document',
                            payment_method='paypal',
                            payment_id=paypal_payment_id,
                            status='completed',
                            generated_form_id=form.id
                        )
                        db.session.add(payment)
                        db.session.commit()
                        
                        flash('Payment successful! You can now download the document.', 'success')
                        return redirect(url_for('preview', form_id=form.id))
                    else:
                        flash('Payment failed. Please try again.', 'danger')
                        
        return render_template('pay_document.html', form=form, case=case)
    
    @app.route('/pricing', methods=['GET', 'POST'])
    def pricing():
        if request.method == 'POST' and current_user.is_authenticated:
            plan = request.form.get('plan')
            if not plan or plan not in ['pay_per_doc', 'unlimited', 'low_income']:
                flash('Invalid plan selected', 'danger')
                return redirect(url_for('pricing'))
                
            payment_method = request.form.get('payment_method')
            payment_id = request.form.get('payment_id')
            
            # Process payment based on plan
            amount = 0
            if plan == 'pay_per_doc':
                # No need to charge now, will charge per document
                current_user.subscription_type = plan
                db.session.commit()
                flash('Subscription updated!', 'success')
                return redirect(url_for('dashboard'))
            elif plan == 'unlimited':
                amount = 50.0
            elif plan == 'low_income':
                amount = 25.0
                
            # Process payment
            if payment_method == 'paypal':
                payment_status = process_paypal_payment(payment_id, amount)
                
                if payment_status == 'completed':
                    # Update user subscription
                    current_user.subscription_type = plan
                    # Set subscription end date to 1 year from now for low_income, 1 month for unlimited
                    if plan == 'low_income':
                        current_user.subscription_end = datetime.utcnow().replace(year=datetime.utcnow().year + 1)
                    else:
                        current_user.subscription_end = datetime.utcnow().replace(month=datetime.utcnow().month + 1)
                        
                    # Record payment
                    payment = Payment(
                        user_id=current_user.id,
                        amount=amount,
                        payment_type='subscription',
                        payment_method='paypal',
                        payment_id=payment_id,
                        status='completed'
                    )
                    db.session.add(payment)
                    db.session.commit()
                    
                    flash('Subscription payment successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Payment failed. Please try again.', 'danger')
            
        return render_template('pricing.html')
    
    @app.route('/chat', methods=['GET', 'POST'])
    @login_required
    def chat():
        # Get or create a chat session
        case_id = request.args.get('case_id')
        
        if case_id:
            case = Case.query.get_or_404(int(case_id))
            # Check if user owns the case
            if case.user_id != current_user.id:
                abort(403)
                
            # Look for existing session for this case
            chat_session = ChatSession.query.filter_by(
                user_id=current_user.id,
                case_id=case.id
            ).first()
            
            if not chat_session:
                chat_session = ChatSession(
                    user_id=current_user.id,
                    case_id=case.id
                )
                db.session.add(chat_session)
                db.session.commit()
        else:
            # Look for general session without case
            chat_session = ChatSession.query.filter_by(
                user_id=current_user.id,
                case_id=None
            ).first()
            
            if not chat_session:
                chat_session = ChatSession(
                    user_id=current_user.id,
                    case_id=None
                )
                db.session.add(chat_session)
                db.session.commit()
        
        # Get chat history
        messages = ChatMessage.query.filter_by(session_id=chat_session.id).order_by(ChatMessage.timestamp).all()
        
        # Get user's cases for context
        user_cases = Case.query.filter_by(user_id=current_user.id).all()
        
        return render_template('chat.html', session=chat_session, messages=messages, cases=user_cases)
    
    @app.route('/api/chat', methods=['POST'])
    @login_required
    def api_chat():
        data = request.json
        message = data.get('message')
        session_id = data.get('session_id')
        
        if not message or not session_id:
            return jsonify({'error': 'Missing message or session ID'}), 400
            
        # Get the chat session
        chat_session = ChatSession.query.get(session_id)
        if not chat_session or chat_session.user_id != current_user.id:
            return jsonify({'error': 'Invalid session'}), 403
            
        # Save user message
        user_message = ChatMessage(
            session_id=session_id,
            is_user=True,
            message=message
        )
        db.session.add(user_message)
        
        # Get context for AI response
        context = {}
        if chat_session.case_id:
            case = Case.query.get(chat_session.case_id)
            documents = Document.query.filter_by(case_id=case.id).all()
            context = {
                'case': case,
                'documents': documents
            }
            
        # Generate AI response
        ai_response = generate_ai_response(message, context)
        
        # Save AI response
        ai_message = ChatMessage(
            session_id=session_id,
            is_user=False,
            message=ai_response
        )
        db.session.add(ai_message)
        db.session.commit()
        
        return jsonify({
            'response': ai_response,
            'user_message_id': user_message.id,
            'ai_message_id': ai_message.id
        })
    
    @app.route('/api/document_upload', methods=['POST'])
    @login_required
    def api_document_upload():
        # Check if case_id exists
        case_id = request.form.get('case_id')
        if not case_id:
            return jsonify({'error': 'No case ID provided'}), 400
            
        case = Case.query.get_or_404(int(case_id))
        
        # Check if user owns the case
        if case.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
            
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        
        if file and allowed_file(file.filename):
            # Create unique filename
            original_filename = secure_filename(file.filename)
            file_extension = original_filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            
            # Create user directory if it doesn't exist
            user_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id))
            os.makedirs(user_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(user_dir, unique_filename)
            file.save(file_path)
            
            # Process document with OCR
            extracted_text, metadata = process_document(file_path, file_extension)
            
            # Save document info to database
            new_document = Document(
                user_id=current_user.id,
                case_id=case.id,
                filename=original_filename,
                file_path=file_path,
                file_type=file_extension,
                extracted_text=extracted_text,
                doc_metadata=metadata
            )
            db.session.add(new_document)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'document_id': new_document.id,
                'filename': original_filename
            })
        else:
            return jsonify({'error': 'Invalid file type'}), 400
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
        
    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500
