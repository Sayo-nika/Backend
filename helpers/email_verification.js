/**
* @file email_verification.js
* @author Capuccino
* @license BSD-3-Clause
*/

const {json} = require("micro");
const redis = require("redis");
const redite = require("redite");
const db = new Redite();
const tokenGenerator = require("jwt-generator");
const mailer = require("nodemailer").createTransport({
    host: config.host,
    port: 465,
    secure: true,
    auth: {
        user: config.auth.user,
        pass: config.auth.password
    }
});

module.exports = async req => {
    const data = await json(req);
}