"""Create the initial NAVISAIL domain schema."""

from app.db.base import Base
from sqlalchemy import text

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables from the canonical SQLAlchemy metadata."""
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        bind.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    """Drop all Phase 2 tables."""
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
