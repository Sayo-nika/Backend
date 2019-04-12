/**
 * @file Background service for automatically deleting unverified accounts after 24 hours.
 * @author Ovyerus
 */

const {Client} = require("pg");

const thirtyMinutes = 1000 * 60 * 30;

// TODO: see if it's possible to automate this by attaching conditional TTLs or some sort of database event.
module.exports = ({host, port, database, user, password}) => {
    const client = new Client({
        host,
        port,
        database,
        user,
        password
    });

    client.connect(err => {
        if (err) throw err;

        setTimeout(async () => (
            // DELETE any user accounts which don't have a verified email and are older than 24 hours.
            await client.query("DELETE FROM users WHERE email_verified = false AND now() - created_at > interval '24 hours';")
        ), thirtyMinutes);
    });
};
