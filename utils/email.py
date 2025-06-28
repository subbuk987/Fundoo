from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from config.config_loader import email_settings

conf = ConnectionConfig(
    MAIL_USERNAME=email_settings.MAIL_USERNAME,
    MAIL_PASSWORD=email_settings.MAIL_PASSWORD,
    MAIL_FROM=email_settings.MAIL_FROM,
    MAIL_PORT=email_settings.MAIL_PORT,
    MAIL_SERVER=email_settings.MAIL_SERVER,
    MAIL_FROM_NAME=email_settings.MAIL_FROM_NAME,
    MAIL_SSL_TLS=email_settings.MAIL_SSL_TLS,
    MAIL_STARTTLS=email_settings.MAIL_STARTTLS,
    USE_CREDENTIALS=email_settings.USE_CREDENTIALS,
)


async def send_email(subject: str, email_to: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        subtype="html",
    )
    fm = FastMail(conf)
    await fm.send_message(message)
