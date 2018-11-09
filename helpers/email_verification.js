/**
* @file email_verification.js
* @author Capuccino
* @license BSD-3-Clause
*/

const micro = require("micro");
const {json} = micro;
const redis = require("redis");
const Redite = require("redite");
const config = require("./email.config");
const snowflake = require("snowflake-codon");
const client = redis.createClient();
const db = new Redite({client});
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

const server = micro(async req => {
    const data = await json(req);
    // generate a token, add it to redis
    let id = idGen.nextId();
    client.hset(data.user.name, `email_verification`, JSON.stringify({
        deleteThis: true,
        id
    }), async err => {
        if (err) send(res, 500, `{code: 500, message: ${err}`);

        // While we have this on urlencoded, the Redis entry serves as a verification point.
        // We want to confirm if this is created by us or maliciously created by someone.
        // However, this is handled by the REST Server, and not this microservice.

        else mailer.sendMail({
            to: `${data.user.name} <${data.user.email}>`,
            subject: 'Welcome to Sayonika - Confirm your email!',
            html: `
              <p align="center">Hey there, we would like to welcome you in Sayonika!</p>
              <br>
              <p align="center">
                As a security measure we would like to ask you to confirm your account.
                Your account won't be accessible if you don't confirm for 24 hours.
              </p>
              <br>
              <center><a href="${config.url}/api/v1/verify?token=${id}">Click to confirm your account</a></center>
              <br>
              <p align="center">If you have questions, do not hesitate to ask us on <code>hello@sayonika.moe</code>.</p>

              <p align="left">Happy Modding!</p>
            `
        }, async(err, info) => {
             if (err) send(res, 500, '{"code": 500, "message": "failed to send to subject."}');
             else send(res, 200, '{"code": 200, "message": "Transport to subject successful"}');
             mailer.close(); 
        });
    });
    // expire token by 24 hours.
    client.expireat(data.username, parseInt((+new Date)/1000) + 86400);
});

server.listen(3000);