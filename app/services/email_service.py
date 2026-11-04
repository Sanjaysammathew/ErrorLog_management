import httpx

from app.core.config import settings
from app.exceptions.custom_exceptions import EmailDeliveryError
from app.models.error_ticket import ErrorTickets
from app.models.user import user


class EmailService:
    MAILJET_SEND_URL = "https://api.mailjet.com/v3.1/send"

    def __init__(self) -> None:
        self.api_key = settings.MAILJET_API_KEY
        self.api_secret = (
            settings.MAILJET_API_SECRET.get_secret_value()
            if settings.MAILJET_API_SECRET is not None
            else None
        )
        self.sender_email = settings.MAILJET_FROM or settings.MAIL_FROM
        self.sender_name = settings.MAIL_FROM_NAME

    async def send_email(
        self,
        recipient_email: str,
        subject: str,
        text_part: str,
        html_part: str | None = None,
        sender_email: str | None = None,
    ) -> None:
        message_sender = sender_email or self.sender_email
        if not self.api_key or not self.api_secret or not message_sender:
            raise EmailDeliveryError("Mailjet email settings are not configured")

        message = {
            "From": {"Email": message_sender, "Name": self.sender_name},
            "To": [{"Email": recipient_email}],
            "Subject": subject,
            "TextPart": text_part,
        }
        if html_part is not None:
            message["HTMLPart"] = html_part

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.MAILJET_SEND_URL,
                    auth=(self.api_key, self.api_secret),
                    json={"Messages": [message]},
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise EmailDeliveryError(
                f"Mailjet rejected the email (HTTP {exc.response.status_code})"
            ) from exc
        except httpx.RequestError as exc:
            raise EmailDeliveryError("Mailjet could not be reached") from exc

    async def send_account_created(self, new_user: user) -> None:
        await self.send_email(
            new_user.email,
            "Your ErrorLog account was created",
            (
                f"Hello {new_user.username},\n\n"
                "Your ErrorLog employee account has been created. "
                "Please contact the administrator for your login password."
            ),
        )

    async def send_ticket_created(self, ticket: ErrorTickets) -> None:
        if ticket.created_by_user is None:
            raise EmailDeliveryError("Ticket owner is unavailable for notification")
        await self.send_email(
            ticket.created_by_user.email,
            f"New ticket created: {ticket.ticket_number}",
            (
                f"A new ticket was created.\n\n"
                f"Ticket: {ticket.ticket_number}\n"
                f"Title: {ticket.title}\n"
                f"Status: {ticket.status}\n"
            ),
        )

    async def send_ticket_closed(self, ticket: ErrorTickets) -> None:
        if ticket.created_by_user is None:
            raise EmailDeliveryError("Ticket owner is unavailable for notification")
        await self.send_email(
            ticket.created_by_user.email,
            f"Ticket closed: {ticket.ticket_number}",
            (
                f"Your ticket {ticket.ticket_number} has been closed.\n\n"
                f"Title: {ticket.title}\n"
                f"Status: {ticket.status}\n"
            ),
        )

    async def send_approval_decision(
        self,
        ticket: ErrorTickets,
        status: str,
        decision_reason: str | None,
    ) -> None:
        if ticket.assigned_admin is None:
            raise EmailDeliveryError("Assigned admin is unavailable for notification")
        if not settings.MAILJET_APPROVAL_FROM:
            raise EmailDeliveryError(
                "Mailjet approval sender is not configured"
            )

        reason = decision_reason or "No reason was provided."
        await self.send_email(
            ticket.assigned_admin.email,
            f"Ticket {status}: {ticket.ticket_number}",
            (
                f"Manager decision: {status}\n\n"
                f"Ticket: {ticket.ticket_number}\n"
                f"Title: {ticket.title}\n"
                f"Status: {ticket.status}\n"
                f"Reason: {reason}\n"
            ),
            sender_email=settings.MAILJET_APPROVAL_FROM,
        )
