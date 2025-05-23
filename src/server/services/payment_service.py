from datetime import datetime
from flask import flash, redirect, url_for, request
from src.models import db, Payment, Case
from src.server.extensions import send_receipt
from src.server.payments import verify_paypal_payment

def confirm_e_transfer(case_id, user):
    case = Case.query.filter_by(id=case_id, user_id=user.id).first()
    if not case:
        flash("Access denied.", "danger")
        return redirect(url_for("main.dashboard"))

    case.is_paid = True
    db.session.commit()

    payment = Payment(
        case_id=case.id,
        user_id=user.id,
        amount=9.99,
        payment_type="legal_package",
        payment_method="e-transfer",
        status="completed",
        created_at=datetime.utcnow()
    )
    db.session.add(payment)
    db.session.commit()

    send_receipt(user.email, case.title, "e-transfer")
    flash("Payment confirmed. You can now download your documents.", "success")
    return redirect(url_for("main.review_case", case_id=case.id))

def confirm_paypal_payment(req, case_id, user):
    case = Case.query.filter_by(id=case_id, user_id=user.id).first()
    if not case:
        flash("Access denied.", "danger")
        return redirect(url_for("main.dashboard"))

    order_id = req.form.get("order_id")
    if not order_id:
        flash("Missing PayPal order ID.", "danger")
        return redirect(url_for("main.review_case", case_id=case.id))

    status = verify_paypal_payment(order_id, 9.99)
    if status == "completed":
        case.is_paid = True
        db.session.commit()

        payment = Payment(
            case_id=case.id,
            user_id=user.id,
            amount=9.99,
            payment_type="legal_package",
            payment_method="paypal",
            payment_id=order_id,
            status="completed",
            created_at=datetime.utcnow()
        )
        db.session.add(payment)
        db.session.commit()

        send_receipt(user.email, case.title, "PayPal")
        flash("Payment confirmed. You can now download your documents.", "success")
    else:
        flash("PayPal payment could not be verified.", "danger")

    return redirect(url_for("main.review_case", case_id=case.id))
