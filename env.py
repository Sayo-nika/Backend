# Stdlib
from logging.config import fileConfig
import os
import sys

# External Libraries
from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# Sayonika Internals
from framework.db import db as target_metadata  # isort:skip
from framework.objects import SETTINGS  # isort:skip

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    return URL(
        "postgres",
        username=SETTINGS["DB_NAME"],
        password=SETTINGS["DB_PASS"],
        host=SETTINGS["DB_HOST"],
        port=SETTINGS["DB_PORT"],
        database=SETTINGS["DB_NAME"]
    )


def run_migrations_offline():
    """
    Run migrations in 'offline' mode. Run when passing the `--sql flag to alembic.
    Outputs an SQL string which is used to upgrade/downgrade a database, instead of working on it through alembic.
    """
    url = get_url()
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """
    Run migrations in 'online' mode.
    Connects to the given database and automatically applies the wanted upgrades/downgrades.
    """
    connectable = create_engine(get_url())

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
