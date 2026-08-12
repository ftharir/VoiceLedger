"""add domains and knowledge entries

Revision ID: b7768a8fafa8
Revises: 03fb40ca3d19
Create Date: 2026-08-12 21:29:55.851282

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b7768a8fafa8"
down_revision: Union[str, Sequence[str], None] = "03fb40ca3d19"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create domains table
    op.create_table(
        "domains",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_domains_slug"),
        "domains",
        ["slug"],
        unique=True,
    )

    # 2. Seed the default technical domain safely.
    # ON CONFLICT keeps this operation idempotent by slug.
    op.execute(
        sa.text(
            """
            INSERT INTO domains (
                name,
                slug,
                description,
                is_active
            )
            VALUES (
                'فنی',
                'technical',
                NULL,
                true
            )
            ON CONFLICT (slug) DO NOTHING
            """
        )
    )

    # 3. Add domain_id as nullable first.
    # Existing voice_reports do not have a domain yet.
    op.add_column(
        "voice_reports",
        sa.Column(
            "domain_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    # 4. Backfill all existing voice reports to the default technical domain.
    op.execute(
        sa.text(
            """
            UPDATE voice_reports
            SET domain_id = (
                SELECT id
                FROM domains
                WHERE slug = 'technical'
            )
            WHERE domain_id IS NULL
            """
        )
    )

    # 5. After backfill, domain_id can safely become required.
    op.alter_column(
        "voice_reports",
        "domain_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.create_index(
        op.f("ix_voice_reports_domain_id"),
        "voice_reports",
        ["domain_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_voice_reports_domain_id_domains",
        "voice_reports",
        "domains",
        ["domain_id"],
        ["id"],
    )

    # 6. Create common knowledge base table.
    op.create_table(
        "knowledge_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("domain_id", sa.Integer(), nullable=False),
        sa.Column("entry_type", sa.String(length=50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["domain_id"],
            ["domains.id"],
            name="fk_knowledge_entries_domain_id_domains",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_knowledge_entries_user_id_users",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_knowledge_entries_domain_id"),
        "knowledge_entries",
        ["domain_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_knowledge_entries_entry_type"),
        "knowledge_entries",
        ["entry_type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_knowledge_entries_id"),
        "knowledge_entries",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_knowledge_entries_source_id"),
        "knowledge_entries",
        ["source_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_knowledge_entries_user_id"),
        "knowledge_entries",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    # Remove knowledge base first because it depends on domains/users.
    op.drop_index(
        op.f("ix_knowledge_entries_user_id"),
        table_name="knowledge_entries",
    )

    op.drop_index(
        op.f("ix_knowledge_entries_source_id"),
        table_name="knowledge_entries",
    )

    op.drop_index(
        op.f("ix_knowledge_entries_id"),
        table_name="knowledge_entries",
    )

    op.drop_index(
        op.f("ix_knowledge_entries_entry_type"),
        table_name="knowledge_entries",
    )

    op.drop_index(
        op.f("ix_knowledge_entries_domain_id"),
        table_name="knowledge_entries",
    )

    op.drop_table("knowledge_entries")

    # Remove VoiceReport dependency on domains.
    op.drop_constraint(
        "fk_voice_reports_domain_id_domains",
        "voice_reports",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_voice_reports_domain_id"),
        table_name="voice_reports",
    )

    op.drop_column(
        "voice_reports",
        "domain_id",
    )

    # Finally remove domains.
    op.drop_index(
        op.f("ix_domains_slug"),
        table_name="domains",
    )

    op.drop_table("domains")