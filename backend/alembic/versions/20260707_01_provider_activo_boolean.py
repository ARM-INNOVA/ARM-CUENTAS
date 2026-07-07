"""provider activo integer to boolean

Revision ID: 20260707_01_provider_activo_boolean
Revises: 
Create Date: 2026-07-07
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "20260707_01_provider_activo_boolean"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE providers
        ALTER COLUMN activo TYPE boolean
        USING activo::integer::boolean
        """
    )
    op.execute("UPDATE providers SET activo = true WHERE activo IS NULL")
    op.execute("ALTER TABLE providers ALTER COLUMN activo SET DEFAULT true")
    op.execute("ALTER TABLE providers ALTER COLUMN activo SET NOT NULL")


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE providers
        ALTER COLUMN activo TYPE integer
        USING CASE WHEN activo THEN 1 ELSE 0 END
        """
    )
    op.execute("ALTER TABLE providers ALTER COLUMN activo SET DEFAULT 1")
    op.execute("UPDATE providers SET activo = 1 WHERE activo IS NULL")
    op.execute("ALTER TABLE providers ALTER COLUMN activo SET NOT NULL")
