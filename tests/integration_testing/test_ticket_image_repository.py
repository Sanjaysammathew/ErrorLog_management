import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.error_ticket import ErrorTickets
from app.models.ErrorCategory import ErrorCategory, IssueType
from app.models.ticket_image import TicketImage
from app.models.user import user
from app.repositories.implementations.ticket_image_repository import (
    TicketImageRepository,
)


async def create_ticket(db_session):
    category = ErrorCategory(
        name="Image Test Category",
        issue_type=IssueType.HARDWARE,
        default_sla_hours=24,
    )
    db_session.add(category)
    await db_session.flush()
    employee = await db_session.scalar(
        select(user).where(user.email == "employee@example.com")
    )
    ticket = ErrorTickets(
        ticket_number="IMG-TICKET-1",
        title="Image attachment ticket",
        category_id=category.id,
        user_id=employee.id,
        assigned_admin_id=1,
    )
    db_session.add(ticket)
    await db_session.commit()
    await db_session.refresh(ticket)
    return ticket, employee


def make_image(ticket_id: int, uploaded_by_id: int, *, path="/tmp/ticket.png"):
    return TicketImage(
        ticket_id=ticket_id,
        uploaded_by_id=uploaded_by_id,
        original_filename="ticket.png",
        file_path=path,
        content_type="image/png",
        size_bytes=128,
    )


@pytest.mark.asyncio(loop_scope="session")
async def test_create_image_persists_attachment_metadata(db_session):
    repository = TicketImageRepository(db_session)
    ticket, employee = await create_ticket(db_session)
    image = await repository.create_image(make_image(ticket.id, employee.id))
    persisted = await db_session.scalar(
        select(TicketImage).where(TicketImage.id == image.id)
    )

    assert image.id is not None
    assert persisted is not None
    assert persisted.ticket_id == ticket.id
    assert persisted.uploaded_by_id == employee.id
    assert persisted.original_filename == "ticket.png"
    assert persisted.size_bytes == 128


@pytest.mark.asyncio(loop_scope="session")
async def test_get_image_by_id_retrieves_persisted_attachment(db_session):
    repository = TicketImageRepository(db_session)
    ticket, employee = await create_ticket(db_session)
    image = await repository.create_image(
        make_image(ticket.id, employee.id, path="/tmp/retrievable.png")
    )

    found = await repository.get_image_by_id(image.id)

    assert found is not None
    assert found.file_path == "/tmp/retrievable.png"
    assert found.ticket_id == ticket.id


@pytest.mark.asyncio(loop_scope="session")
async def test_get_image_by_id_returns_none_for_missing_attachment(db_session):
    repository = TicketImageRepository(db_session)

    assert await repository.get_image_by_id(999999) is None


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_image_removes_persisted_attachment(db_session):
    repository = TicketImageRepository(db_session)
    ticket, employee = await create_ticket(db_session)
    image = await repository.create_image(
        make_image(ticket.id, employee.id, path="/tmp/delete-me.png")
    )

    await repository.delete_image(image)
    persisted = await db_session.scalar(
        select(TicketImage).where(TicketImage.id == image.id)
    )

    assert persisted is None


@pytest.mark.asyncio(loop_scope="session")
async def test_create_duplicate_image_path_raises_integrity_error(db_session):
    repository = TicketImageRepository(db_session)
    ticket, employee = await create_ticket(db_session)
    await repository.create_image(
        make_image(ticket.id, employee.id, path="/tmp/unique-image.png")
    )

    with pytest.raises(IntegrityError):
        await repository.create_image(
            make_image(ticket.id, employee.id, path="/tmp/unique-image.png")
        )

    assert await db_session.scalar(
        select(TicketImage).where(TicketImage.file_path == "/tmp/unique-image.png")
    ) is not None
    assert len((await db_session.scalars(select(TicketImage))).all()) == 1
