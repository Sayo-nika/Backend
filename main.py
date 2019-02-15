# Stdlib
import sys

# External Libraries
from sqlalchemy.engine.url import URL

# Sayonika Internals
from framework.objects import SETTINGS, db, sayonika_instance, loop


async def setup_gino():
    await db.set_bind(URL("asyncpg", username=SETTINGS["DB_NAME"], password=SETTINGS["DB_PASS"],
                          host=SETTINGS["DB_HOST"], port=SETTINGS["DB_PORT"], database=SETTINGS["DB_NAME"]))
    await db.gino.create_all()


sayonika_instance.debug = (len(sys.argv) > 1 and sys.argv[1] == "--debug")
sayonika_instance.gather("routes")
loop.run_until_complete(setup_gino())

try:
    sayonika_instance.run(SETTINGS["SERVER_BIND"], int(SETTINGS["SERVER_PORT"]), loop=loop)
except KeyboardInterrupt:
    # Stop big stack trace getting printed when interrupting
    pass
