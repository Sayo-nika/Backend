/**
 * @file av_worker.js
 * @author Capuccino
 * @license BSD-3-Clause
 */
global.Promise = require("bluebird");
const micro = require("micro");
const https = require("https");
const {json, send} = micro;
const config = require('./av.config');

const server = micro(async (req, res) => {
     const data = json(req);

     request('POST', `https://www.virustotal.com/vtapi/v2/url/scan?apikey=${config.apiKey}`, {}, {}).then(res => {

        if (res.statusCode === '204') send(res, 204, JSON.stringify({code: "204", reason: "Exceeded VirusTotal Ratelimit."}));
        // TODO: Check to VT if its a safe file.
        // because this one returns only a permalink.
        else send(res, 200, JSON.stringify(res));
     })
});

server.listen(parseInt(config.port));

// simple request function for creating a Promisified HTTP/S request.
function request(method, url, options={}, payload) {
    return new Promise((resolve, reject) => {
        let req = https.request(Object.assign(URL.parse(url), options, {method}), res => {
            let chunked = '';

            if (res.statusCode !== 200) return reject(new Error(`HTTP ${res.statusCode}: ${res.statusMessage}`));

            res.setEncoding('utf8');
            res.on('data', chunk => chunked += chunk);
            res.on('error', reject);
            res.on('end', () => {
                let val;

                try {
                    val = JSON.parse(chunked);
                } catch(e) {
                    return resolve(chunked);
                }

                if (val.error) return reject(new Error(val.error));
                else return resolve(val);
            });
        });

        req.on('error', reject);
        if (payload) req.write(payload);
        req.end();
    });
}