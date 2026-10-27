"""Create the persistent bounded notes schema."""

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create constrained note storage and one capacity-serialization row."""
    op.execute("CREATE TABLE notes (id uuid PRIMARY KEY, ordinal bigint GENERATED ALWAYS AS IDENTITY UNIQUE, title text NOT NULL CHECK (length(btrim(title)) BETWEEN 1 AND 120), body text NOT NULL CHECK (length(body)<=10000))")
    op.execute("CREATE TABLE capacity_guard (id integer PRIMARY KEY CHECK (id=1))")
    op.execute("INSERT INTO capacity_guard(id) VALUES(1)")


def downgrade() -> None:
    """Refuse implicit destructive downgrade; use a reviewed generation restore."""
    raise RuntimeError("Use the managed database restore workflow.")
