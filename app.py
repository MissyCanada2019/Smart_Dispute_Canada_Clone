from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    # Mock test data for now
    cases = [
        {
            "title": "Tenant Dispute - Rent Increase",
            "merit_score": 0.85,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "category": "Housing",
            "status": "in_review",
            "documents": ["lease.pdf", "notice.png"]
        },
        {
            "title": "Credit Report Error",
            "merit_score": 0.72,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "category": "Credit",
            "status": "awaiting_documents",
            "documents": []
        }
    ]

    current_user = {
        "subscription_type": "free",
        "subscription_end": datetime(2025, 12, 31)
    }

    return render_template("dashboard.html", cases=cases, current_user=current_user)

if __name__ == "__main__":
    app.run()
