"""Run reviewed migrations with the selected migration-role connection."""

from alembic import context

from fastapi_app.services.database import Database

with Database().engine.connect() as connection:
    context.configure(connection=connection, target_metadata=None)
    with context.begin_transaction():
        context.run_migrations()
