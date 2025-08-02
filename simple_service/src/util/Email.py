import aiosmtplib
from email.message import EmailMessage

async def send_email(
    smtp_client: aiosmtplib.SMTP,
    frm,
    to,
    subject,
    body
):
    async with smtp_client:
        message = EmailMessage()
        message["From"] = frm
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)
        await smtp_client.send_message(message)