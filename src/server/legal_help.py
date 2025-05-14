from flask import Blueprint, render_template, jsonify
from src.models import Case, Evidence

legal_help_bp = Blueprint("legal_help", __name__)

@legal_help_bp.route("/legal-help")
def legal_help():
    return render_template("legal_help.html")

@legal_help_bp.route("/legal-help/data")
def legal_help_data():
    return jsonify({"message": "Legal help topics will appear here dynamically."})
