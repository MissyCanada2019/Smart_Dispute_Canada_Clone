from src.server import create_app
from src.server.extensions import db
from src.models import FormTemplate
from scripts.scrape_ontario_forms import scrape_ontario_forms

app = create_app()

with app.app_context():
    forms = scrape_ontario_forms()
    for form in forms:
        exists = FormTemplate.query.filter_by(name=form["name"], url=form["url"]).first()
        if not exists:
            new_form = FormTemplate(**form)
            db.session.add(new_form)
    db.session.commit()
    print(f"Loaded {len(forms)} forms into the database.")
