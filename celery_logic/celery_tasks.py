from celery_logic.celery_worker import celery_app
from utils.email import send_email
from db.database import get_db
from models.note import Note
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer
from config.config_loader import email_settings


serializer = URLSafeTimedSerializer(
    secret_key=email_settings.EMAIL_JWT_SECRET, salt="email-verification-salt"
)


def create_url_safe_token(data: dict):
    token = serializer.dumps(data)

    return token


def decode_url_safe_token(token: str):
    token_data = serializer.loads(token)

    return token_data


@celery_app.task
def send_verification_email_task(username: str, email: str):
    import asyncio
    token = create_url_safe_token(
        {"email": email, "username": username}
    )
    link = f"https://{email_settings.DOMAIN}/api/v1/auth/verify/{token}"

    html = f"""
        <h1>Verify your Email</h1>
        <p>Please click this <a href="{link}">link</a> to verify your email</p>
        """
    asyncio.run(send_email(
        subject="Verify your email - Fundoo",
        email_to=email,
        body=html
    ))


@celery_app.task
def notify_expiring_notes_task():
    db: Session = next(get_db())
    target_date = datetime.now() + timedelta(days=1)

    notes = db.query(Note).filter(Note.expiry <= target_date).all()

    for note in notes:
        user = note.user
        import asyncio
        asyncio.run(send_email(
            subject="Note Expiry Reminder",
            email_to=user.email,
            body=f"<p>Your note titled '<b>{note.title}</b>' is set to expire tomorrow ({note.expiry.date()}).</p>"
        ))

    db.close()
