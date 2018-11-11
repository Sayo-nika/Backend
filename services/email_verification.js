/**
* @file email_verification.js
* @author Capuccino
* @license BSD-3-Clause
*/

global.Promise = require("bluebird");
const micro = require("micro");
const {json, send} = micro;
const redis = require("redis");
const config = require("./email.config");
const bcrypt = require("bcrypt");
const snowflake = require("snowflake-codon");
const client = redis.createClient({
    host: config.redis.host,
    password: config.redis.password
});

// promisifying Redis so async can acknowledge this

Promise.promisifyAll(redis.RedisClient.prototype);
Promise.promisifyAll(redis.Multi.prototype);

const idGen = new snowflake(12, Math.floor(Math.random() * 1129), 2018, 200);

const mailer = require("nodemailer").createTransport({
    host: config.host,
    port: 465,
    secure: true,
    auth: {
        user: config.auth.user,
        pass: config.auth.password
    }
}, {
    // sender options
    from: 'Sayonika <noreply@sayonika.moe>',
    headers: {
        'X-Powered-by': 'micro',
        'X-Logokas-is': 'hot'
    }
});
/**
 * Checks if a specific object is empty
 * @param {Object} obj Object to analyze.
 * @returns {Boolean} True if non-empty, False if not. 
 */
function isEmpty(obj) {
    for(let key in obj) {
        if(!obj[key]) return false;
    }
    return true;
}

if (isEmpty(config)) return new Error("Config is empty! Exiting.");

const server = micro(async (req, res) => {
    const data = await json(req);
    // generate a token, add it to redis
    const id = idGen.nextId();
    const token = bcrypt.hashSync(`${data.user.email}:${id}`)
    
    try {
      await client.set(`${data.user.email}:email_verify`, token, 'EX', 60 * 60 * 24);

        // While we have this on urlencoded, the Redis entry serves as a verification point.
        // We want to confirm if this is created by us or maliciously created by someone.
        // However, this is handled by the REST Server, and not this microservice.
        // TODO : Check if this a Redis entry exist to prevent resends.
      await mailer.sendMail({
          to: `${data.user.name} <${data.user.email}>`,
          subject: 'Welcome to Sayonika - Confirm your email!',
          html: `
              <html>
               <head>
                 <style>
                   p {
                      text-align: center;
                   } 
                   a {
                       text-align: center;
                   }
                 </style>
               </head>
              <body>
              <p>Hey there, we would like to welcome you in Sayonika!</p>
              <br>
              <p>
                As a security measure we would like to ask you to confirm your account.
                You will not be able to access your account if you don't confirm your email within 24 hours.
              </p>
              <br>
              <a href="${config.url}/api/v1/verify?token=${token}">Click to confirm your account</a>
              <br>
              <p >If you have questions, do not hesitate to ask us on <a href="mailto:hello@sayonika.moe">hello@sayonika.moe</a>.</p>

              <p>Happy Modding!</p>
              </body>
            `
        });

        send(res, 200, JSON.stringify({code: "200", message: `Sent to ${data.user.name} via email (${data.user.email}).`}));
    } catch (err) {
        send(res, 500, JSON.stringify({code: "500", message: `Failed to send attachment. Reason: ${err}`}));
    }
});
server.listen(config.port)