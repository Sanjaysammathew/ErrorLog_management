from datetime import datetime


def generate_ticket_number(ticket_id: int, created_at: datetime) -> str:
    """Build a stable, unique ticket number from its database ID and year."""
    return f"ERR-{created_at.year}-{ticket_id:03d}"
