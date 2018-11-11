/**
* @file email_verification.js
* @author Capuccino
* @license BSD-3-Clause
*/

global.Promise = require("bluebird");
const micro = require("micro");
const {json} = micro;
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

const server = micro(async req => {
    const data = await json(req.body);
    // generate a token, add it to redis
    let id = idGen.nextId();
    let token = bcrypt.hashSync(`${data.user.email}:${id}`)
    client.set(`${data.user.email}:email_verify`, token, async err => {

        if (err) send(res, 500, `{"code": "500", "message": ${err}`);

        // While we have this on urlencoded, the Redis entry serves as a verification point.
        // We want to confirm if this is created by us or maliciously created by someone.
        // However, this is handled by the REST Server, and not this microservice.
        // TODO : Check if this a Redis entry exist to prevent resends.

        else mailer.sendMail({
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
        }, async(err, info) => {
             if (err) send(res, 500, `{"code": "500", "message": "failed to send to subject. Reason: ${err}"}`);
             else send(res, 200, '{"code": "200", "message": "Transport to subject successful"}');
             mailer.close();
        });
    });
    // expire token by 24 hours.
    client.expireat(data.user.name, parseInt((+new Date)/1000) + 86400);
});

server.listen(config.port);