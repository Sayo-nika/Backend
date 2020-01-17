# Environment Variables

The server uses several environment variables in order to run correctly. All of these should be prefixed with the phrase `SAYONIKA_` in order for the program to be able to determine what variables to use.

-   `DB_HOST`: IP/domain of database to connect to. (Default: `localhost`)
-   `DB_PORT`: Port of the database to connect to. (Default: `5432`)
-   `DB_USER`: Name of the database user to use. (Default: `sayonika`)
-   `DB_PASS`: Password of the database user to use. (Default: `sayonika`)
-   `DB_NAME`: Name of the database to use (Default: `sayonika`)
-   `JWT_SECRET`: Secret to use for signing and verifying tokens (Default: `testing123`)
-   `REDIS_URL`: URL of the Redis instance to connect to. (Default: `redis://localhost:6379/0`)
-   `EMAIL_BASE`: Base URL used in emails. (Default: `http://localhost:4444`)
-   `RATELIMITS`: A semicolon (`;`) delimited string of what ratelimits to apply (Default: `1 per 2 seconds;20 per minute;1000 per hour`) (See: https://flask-limiter.readthedocs.io/en/stable/#rate-limit-string-notation)
-   `RECAPTCHA_KEY`: Secret key to use for validating reCAPTCHA.
-   `AES_KEY`: 32 bit secret key to use for encryption (usually tracebacks). (Default: `this is a pretty long key oh no`)
-   `MAILGUN_KEY`: Token to use for sending mail via Mailgun.
