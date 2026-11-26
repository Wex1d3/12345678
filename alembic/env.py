from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.core.config import settings
from app.db.base import Base
from app import models  # noqa: F401
import os

config = context.config

# --- ИСПРАВЛЕНИЕ НАЧАЛО ---
# Берем URL из Railway (переменная DATABASE_URL), а если её нет — из твоих настроек
db_url = os.getenv("DATABASE_URL")
if db_url:
    # Railway иногда отдает postgres://, а SQLAlchemy 2.x требует postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    config.set_main_option("sqlalchemy.url", db_url)
else:
    config.set_main_option("sqlalchemy.url", settings.database_url)
# --- ИСПРАВЛЕНИЕ КОНЕЦ ---

if config.config_file_name: 
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction(): 
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction(): 
            context.run_migrations()

if context.is_offline_mode(): 
    run_migrations_offline()
else: 
    run_migrations_online()