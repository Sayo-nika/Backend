# External Libraries
from aioredis.commands import Redis


class InitLaterRedis(Redis):  # pylint: disable=abstract-method,too-many-ancestors
    """An extension of aioredis commands to allow you to create it somewhere and then init it later."""

    async def setup(self):
        pool = self._pool_or_conn

        try:
            await pool._fill_free(override_min=False)  # pylint: disable=protected-access
        except Exception:
            pool.close()
            await pool.wait_closed()
            await pool.wait_closed()
            raise
