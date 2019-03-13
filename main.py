# Stdlib
import sys

# External Libraries
from sqlalchemy.engine.url import URL

# Sayonika Internals
from framework.objects import SETTINGS, db, loop, redis, sayonika_instance


async def setup_db():
    # Set binding for Gino and init Redis
    await db.set_bind(URL(
        "postgres",
        username=SETTINGS["DB_NAME"],
        password=SETTINGS["DB_PASS"],
        host=SETTINGS["DB_HOST"],
        port=SETTINGS["DB_PORT"],
        database=SETTINGS["DB_NAME"]
    ))

    await redis.setup()


sayonika_instance.debug = (len(sys.argv) > 1 and sys.argv[1] == "--debug")
sayonika_instance.gather("routes")
loop.run_until_complete(setup_db())

try:
    sayonika_instance.run(SETTINGS["SERVER_BIND"], int(SETTINGS["SERVER_PORT"]), loop=loop)
except KeyboardInterrupt:
    # Stop big stack trace getting printed when interrupting
    pass
