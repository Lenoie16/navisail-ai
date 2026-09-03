"""Initial PostgreSQL/PostGIS-compatible persistence schema."""

from alembic import op
from sqlalchemy import Table, event

from app.db.base import Base

revision = "0001_initial_persistence"
down_revision = None
branch_labels = None
depends_on = None


@event.listens_for(Table, "before_create", insert=True)
def _preserve_columns_for_spatial_ddl(table: Table, bind: object, **kwargs: object) -> None:
    """Keep GeoAlchemy's column restoration state available during create_all."""
    table.info.setdefault("_saved_columns", table.columns)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
