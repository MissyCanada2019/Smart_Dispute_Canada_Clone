def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///../instance/app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db)
    csrf.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doc_bp)

    @app.shell_context_processor
    def make_shell_context():
        from src.models import User, Case, Evidence, Payment, LegalReference, FormTemplate
        return dict(
            db=db,
            User=User,
            Case=Case,
            Evidence=Evidence,
            Payment=Payment,
            LegalReference=LegalReference,
            FormTemplate=FormTemplate
        )

    return app
