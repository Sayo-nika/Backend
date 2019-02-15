from aioredis.commands import Redis


class InitLaterRedis(Redis):
    """An extension of aioredis commands to allow you to create it somewhere and then init it later."""

    async def setup(self):
        pool = self._pool_or_conn

        try:
            await pool._fill_free(override_min=False)
        except Exception:
            pool.close()
            await pool.wait_closed()
            await pool.wait_closed()
            raise
