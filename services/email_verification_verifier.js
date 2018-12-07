/**
* @file email_verification_verifier.js
* @author Capuccino
* @license BSD-3-Clause
*/

global.Promise = require("bluebird");
const micro = require("micro");
const parse = require("urlencoded-body-parser");
const {send} = micro;
const redis = require("redis");
const config  = require("./email.config");
const client = redis.createClient({
    host: config.redis.host,
    password: config.redis.password
});

// Promisifying for Async
Promise.promisifyAll(redis.RedisClient.prototype);
Promise.promisifyAll(redis.Multi.prototype);

/**
 * Checks if a specific object is empty
 * @param {Object} obj Object to analyze.
 * @returns {Boolean} True if non-empty, False if not. 
 */
function isEmpty(obj) {
    for (let key in obj) {
        if (!obj[key]) return false;
    }
    return true;
}

if (isEmpty(config)) throw new Error("Config is empty! Exiting.");

const server = micro(async (req, res) => {

    // Parses this into a Promise Object.
    const data = await parse(req);

    client.exists(`${data.email}:email_verify`, async reply => {
        if (reply !== 1) send(res, 410, JSON.stringify({code: "410", message: "Token does not exist. It may have expired."}));

        else client.get(`${data.email}:email_verify`, (err, reply) => {
            if (err) { 
                send(res, 500, JSON.stringify({code: "500", message: "Backend Error. SysOps check logs."}));
                throw err;
            } else {

                // compare, then throw error if not match.
                if (reply !== data.token) send(res, 403, JSON.stringify({code: "403", message: `Incorrect token for user ${data.id}`}));
                else { 
                    send(res, 200, JSON.stringify({code: "200", message: "Tokens match. Mark as verify in REST."}));

                    // delete the key to allow more verifications soon
                    // and to prevent current key abuse.
                    client.del(`${data.email}:email_verify`);
                }
            }
        }); 
    });
});

server.listen(parseInt(config.verifierPort));