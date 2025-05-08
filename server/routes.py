# Inside your /generate-legal-package/<int:case_id> route:
from utils.document_generator import generate_legal_form  # already imported

@app.route("/generate-legal-package/<int:case_id>")
@login_required
def generate_legal_package(case_id):
    case = Case.query.get_or_404(case_id)
    if case.user_id != current_user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for("dashboard"))

    paid = Payment.query.filter_by(case_id=case_id, status="completed").first()
    if not paid and current_user.subscription_type != "unlimited":
        return redirect(url_for("pay_for_case", case_id=case.id))

    combined_text = ""
    for ev in case.evidence:
        text, _ = process_document(ev.file_path, ev.filename.split(".")[-1])
        combined_text += text + "\n"

    # Analyze legal issues
    result = extract_legal_issues(combined_text, province_code=current_user.province)
    issues = result['issues']
    keywords = result['keywords_found']
    merit_score = score_merit(issues, province=current_user.province, matched_keywords=keywords)

    # Choose issue category for form generation
    issue_category = next(iter(issues)) if issues else "Small Claims"

    # Fill in user data
    user_fields = {
        "FULL_NAME": current_user.full_name,
        "ADDRESS": current_user.address,
        "PHONE": current_user.phone,
        "POSTAL_CODE": current_user.postal_code,
        "PROVINCE": current_user.province,
        "CASE_TITLE": case.title
    }

    docx_path, pdf_path = generate_legal_form(issue_category, current_user.province, user_fields, case.id)

    # Create ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.write(docx_path, os.path.basename(docx_path))
        zip_file.write(pdf_path, os.path.basename(pdf_path))
        for ev in case.evidence:
            zip_file.write(ev.file_path, os.path.basename(ev.file_path))
    zip_buffer.seek(0)

    flash(f"Merit score: {merit_score:.2f}%", "info")
    return send_file(zip_buffer, mimetype='application/zip',
                     download_name=f"SmartDispute_Package_{case.title}.zip", as_attachment=True)
