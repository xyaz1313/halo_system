"""initial schema — create all tables

Revision ID: f7e601fdbc77
Revises: 
Create Date: 2026-04-07 16:51:03.697813

Fix: populated upgrade()/downgrade() so a fresh database actually gets
tables instead of running a no-op migration.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'f7e601fdbc77'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -- accounts ----------------------------------------------------------
    op.create_table(
        "accounts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("email", sa.String, nullable=False, unique=True, index=True),
        sa.Column("patient_name", sa.String, nullable=False),
        sa.Column("patient_age", sa.Integer, nullable=False),
        sa.Column("patient_diagnosis_stage", sa.String, nullable=False),
        sa.Column("patient_notes", sa.String, nullable=False, server_default=""),
        sa.Column("caretaker_name", sa.String, nullable=True),
        sa.Column("caretaker_email", sa.String, nullable=True),
    )

    # -- calendars ---------------------------------------------------------
    op.create_table(
        "calendars",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("account_id", sa.String(36),
                  sa.ForeignKey("accounts.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("provider", sa.String, nullable=False),
        sa.Column("external_calendar_id", sa.String, nullable=False),
        sa.Column("sync_status", sa.String, nullable=False,
                  server_default="syncing"),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
    )

    # -- anchors -----------------------------------------------------------
    op.create_table(
        "anchors",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("label", sa.String, nullable=False),
        sa.Column("visibility", sa.String, nullable=False),
        sa.Column("owner_account_id", sa.String(36),
                  sa.ForeignKey("accounts.id", ondelete="CASCADE"),
                  nullable=True),
        sa.Column("signal_threshold", sa.Float, nullable=False,
                  server_default="-70.0"),
        sa.Column("status", sa.String, nullable=False,
                  server_default="active"),
    )

    # -- tags --------------------------------------------------------------
    op.create_table(
        "tags",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("account_id", sa.String(36),
                  sa.ForeignKey("accounts.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("label", sa.String, nullable=True),
        sa.Column("status", sa.String, nullable=False,
                  server_default="active"),
    )

    # -- anchor_tag_associations -------------------------------------------
    op.create_table(
        "anchor_tag_associations",
        sa.Column("anchor_id", sa.String(36),
                  sa.ForeignKey("anchors.id", ondelete="CASCADE"),
                  primary_key=True),
        sa.Column("tag_id", sa.String(36),
                  sa.ForeignKey("tags.id", ondelete="CASCADE"),
                  primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )

    # -- notification_preferences ------------------------------------------
    op.create_table(
        "notification_preferences",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("account_id", sa.String(36),
                  sa.ForeignKey("accounts.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("alert_email", sa.String, nullable=False),
        sa.Column("alert_types", sa.JSON, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("notification_preferences")
    op.drop_table("anchor_tag_associations")
    op.drop_table("tags")
    op.drop_table("anchors")
    op.drop_table("calendars")
    op.drop_table("accounts")
