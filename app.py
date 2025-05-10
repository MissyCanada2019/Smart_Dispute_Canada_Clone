def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "your-secret-key"
    # other config...

    db.init_app(app)
    Migrate(app, db)

    # Blueprint registration
    app.register_blueprint(routes)

    return app  # <-- exactly 4 spaces (no tabs or extra spaces)
