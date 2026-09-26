"""Initial migration

Revision ID: 001_initial_migration
Revises: 
Create Date: 2026-09-26 02:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "001_initial_migration"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.Enum("USER", "ADMIN", name="userrole"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    # Diagnostic Centres table
    op.create_table(
        "diagnostic_centres",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_diagnostic_centres_id"), "diagnostic_centres", ["id"], unique=False)
    op.create_index(op.f("ix_diagnostic_centres_name"), "diagnostic_centres", ["name"], unique=False)

    # Diagnostic Tests table
    op.create_table(
        "diagnostic_tests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_diagnostic_tests_id"), "diagnostic_tests", ["id"], unique=False)
    op.create_index(op.f("ix_diagnostic_tests_name"), "diagnostic_tests", ["name"], unique=False)

    # Centre Tests Association table
    op.create_table(
        "centre_tests",
        sa.Column("centre_id", sa.Integer(), nullable=False),
        sa.Column("test_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["centre_id"], ["diagnostic_centres.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["test_id"], ["diagnostic_tests.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("centre_id", "test_id"),
    )

    # Bookings table
    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("test_id", sa.Integer(), nullable=False),
        sa.Column("centre_id", sa.Integer(), nullable=False),
        sa.Column("appointment_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("status", sa.Enum("PENDING", "CONFIRMED", "FAILED", "CANCELLED", name="bookingstatus"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["centre_id"], ["diagnostic_centres.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["test_id"], ["diagnostic_tests.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_bookings_id"), "bookings", ["id"], unique=False)
    op.create_index(op.f("ix_bookings_status"), "bookings", ["status"], unique=False)
    op.create_index(op.f("ix_bookings_user_id"), "bookings", ["user_id"], unique=False)

    # Payments table
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("booking_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("status", sa.Enum("SUCCESS", "FAILED", name="paymentstatus"), nullable=False),
        sa.Column("provider_transaction_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payments_booking_id"), "payments", ["booking_id"], unique=False)
    op.create_index(op.f("ix_payments_id"), "payments", ["id"], unique=False)
    op.create_index(op.f("ix_payments_status"), "payments", ["status"], unique=False)
    op.create_index("uq_payment_booking_success", "payments", ["booking_id"], unique=True, postgresql_where=sa.text("status = 'SUCCESS'"), sqlite_where=sa.text("status = 'SUCCESS'"))

    # Webhook Events table
    op.create_table(
        "webhook_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_webhook_events_event_id"), "webhook_events", ["event_id"], unique=True)
    op.create_index(op.f("ix_webhook_events_id"), "webhook_events", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_webhook_events_id"), table_name="webhook_events")
    op.drop_index(op.f("ix_webhook_events_event_id"), table_name="webhook_events")
    op.drop_table("webhook_events")

    op.drop_index("uq_payment_booking_success", table_name="payments")
    op.drop_index(op.f("ix_payments_status"), table_name="payments")
    op.drop_index(op.f("ix_payments_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_booking_id"), table_name="payments")
    op.drop_table("payments")

    op.drop_index(op.f("ix_bookings_user_id"), table_name="bookings")
    op.drop_index(op.f("ix_bookings_status"), table_name="bookings")
    op.drop_index(op.f("ix_bookings_id"), table_name="bookings")
    op.drop_table("bookings")

    op.drop_table("centre_tests")

    op.drop_index(op.f("ix_diagnostic_tests_name"), table_name="diagnostic_tests")
    op.drop_index(op.f("ix_diagnostic_tests_id"), table_name="diagnostic_tests")
    op.drop_table("diagnostic_tests")

    op.drop_index(op.f("ix_diagnostic_centres_name"), table_name="diagnostic_centres")
    op.drop_index(op.f("ix_diagnostic_centres_id"), table_name="diagnostic_centres")
    op.drop_table("diagnostic_centres")

    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS userrole;")
    op.execute("DROP TYPE IF EXISTS bookingstatus;")
    op.execute("DROP TYPE IF EXISTS paymentstatus;")
