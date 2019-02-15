# Stdlib
import sys

# External Libraries
from aioredis.commands import Redis
from sqlalchemy.engine.url import URL

# Sayonika Internals
from framework.objects import SETTINGS, db, sayonika_instance, loop, redis


async def setup_db():
    # Set binding for Gino, and create all tables.
    await db.set_bind(URL("asyncpg", username=SETTINGS["DB_NAME"], password=SETTINGS["DB_PASS"],
                          host=SETTINGS["DB_HOST"], port=SETTINGS["DB_PORT"], database=SETTINGS["DB_NAME"]))
    await db.gino.create_all()  # TODO: move to Alembic before v1 for proper DB migrations

    await redis.setup()


sayonika_instance.debug = (len(sys.argv) > 1 and sys.argv[1] == "--debug")
sayonika_instance.gather("routes")
loop.run_until_complete(setup_db())

try:
    sayonika_instance.run(SETTINGS["SERVER_BIND"], int(SETTINGS["SERVER_PORT"]), loop=loop)
except KeyboardInterrupt:
    # Stop big stack trace getting printed when interrupting
    pass
