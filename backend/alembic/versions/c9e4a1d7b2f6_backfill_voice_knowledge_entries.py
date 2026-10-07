"""backfill voice knowledge entries

Revision ID: c9e4a1d7b2f6
Revises: b7768a8fafa8

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c9e4a1d7b2f6"
down_revision: Union[str, Sequence[str], None] = "b7768a8fafa8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            INSERT INTO knowledge_entries (
                user_id,
                domain_id,
                entry_type,
                content,
                source_id,
                created_at
            )
            SELECT
                vr.user_id,
                vr.domain_id,
                'voice',
                vr.transcription,
                vr.id,
                vr.created_at
            FROM voice_reports AS vr
            WHERE
                vr.status = 'completed'
                AND vr.transcription IS NOT NULL
                AND BTRIM(vr.transcription) <> ''
                AND NOT EXISTS (
                    SELECT 1
                    FROM knowledge_entries AS ke
                    WHERE
                        ke.entry_type = 'voice'
                        AND ke.source_id = vr.id
                )
            """
        )
    )


def downgrade() -> None:
    # Intentionally no-op.
    #
    # These rows represent real knowledge derived from existing
    # voice reports. Automatically deleting them during downgrade
    # could remove valid user data created after this migration.
    pass