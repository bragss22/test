from __future__ import with_statement
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

config = context.config
fileConfig(config.config_file_name)

# allow environment override for TEST/CI usage
db_url = os.getenv("DATABASE_URL") or os.getenv("TEST_DATABASE_URL") or config.get_main_option("sqlalchemy.url")
config.set_main_option("sqlalchemy.url", db_url)

# import target metadata
from app.db.base import Base  # noqa: E402
target_metadata = Base.metadata

def run_migrations_offline():
	"""Запуск миграций в offline режиме — генерируются SQL-скрипты без подключения."""
	context.configure(url=db_url, target_metadata=target_metadata, literal_binds=True)
	with context.begin_transaction():
		context.run_migrations()

def run_migrations_online():
	"""Запуск миграций в online режиме — выполняются на подключении к БД."""
	connectable = engine_from_config(
		config.get_section(config.config_ini_section),
		prefix='',
		poolclass=pool.NullPool
	)
	with connectable.connect() as connection:
		context.configure(connection=connection, target_metadata=target_metadata)
		with context.begin_transaction():
			context.run_migrations()

if context.is_offline_mode():
	run_migrations_offline()
else:
	run_migrations_online()