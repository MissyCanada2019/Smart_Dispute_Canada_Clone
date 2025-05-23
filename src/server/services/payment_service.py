from datetime import datetime
from src.models import db  # Safe to import at the top
from src.server.extensions import send_receipt
from src.server.payments import verify_paypal_payment

def record_e_transfer_payment(case, user):
    from src.models import Payment  # Moved to avoid circular import

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

def record_paypal_payment(case, user, payment_id, expected_amount=9.99):
    from src.models import Payment  # Same fix here

    status = verify_paypal_payment(payment_id, expected_amount)
    if status == "completed":
        case.is_paid = True
        db.session.commit()

        payment = Payment(
            case_id=case.id,
            user_id=user.id,
            amount=expected_amount,
            payment_type="legal_package",
            payment_method="paypal",
            payment_id=payment_id,
            status="completed",
            created_at=datetime.utcnow()
        )
        db.session.add(payment)
        db.session.commit()

        send_receipt(user.email, case.title, "PayPal")
    return status
