import asyncio
import smtplib
from email.message import EmailMessage

from app.core.config import settings
from app.exceptions.custom_exceptions import EmailDeliveryError
from app.models.error_ticket import ErrorTickets
from app.models.user import ApprovalStatus


class SMTPEmailService:
    def __init__(self) -> None:
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = (
            settings.SMTP_PASSWORD.get_secret_value()
            if settings.SMTP_PASSWORD is not None
            else None
        )
        self.sender_email = settings.MAIL_FROM or self.username
        self.sender_name = settings.MAIL_FROM_NAME

    async def send_approval_decision(
        self,
        ticket: ErrorTickets,
        status: ApprovalStatus,
        decision_reason: str | None,
    ) -> None:
        if ticket.assigned_admin is None:
            raise EmailDeliveryError("Assigned admin is unavailable for notification")
        if not all(
            (
                self.host,
                self.username,
                self.password,
                self.sender_email,
            )
        ):
            raise EmailDeliveryError("SMTP email settings are not configured")

        subject = f"Ticket {status.value}: {ticket.ticket_number}"
        reason = decision_reason or "No reason was provided."
        body = (
            f"Manager decision: {status.value}\n\n"
            f"Ticket: {ticket.ticket_number}\n"
            f"Title: {ticket.title}\n"
            f"Status: {ticket.status}\n"
            f"Reason: {reason}\n"
        )
        message = EmailMessage()
        message["From"] = f"{self.sender_name} <{self.sender_email}>"
        message["To"] = ticket.assigned_admin.email
        message["Subject"] = subject
        message.set_content(body)

        try:
            await asyncio.to_thread(self._send_message, message)
        except (OSError, smtplib.SMTPException) as exc:
            raise EmailDeliveryError("SMTP could not send the approval email") from exc

    def _send_message(self, message: EmailMessage) -> None:
        use_ssl = self.port == 465 or settings.SMTP_USE_SSL
        if use_ssl:
            with smtplib.SMTP_SSL(self.host, self.port, timeout=10) as server:
                server.login(self.username, self.password)
                server.send_message(message)
            return

        with smtplib.SMTP(self.host, self.port, timeout=10) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            server.login(self.username, self.password)
            server.send_message(message)
