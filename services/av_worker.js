/**
 * @file av_worker.js
 * @author Capuccino
 * @license BSD-3-Clause
 */
global.Promise = require("bluebird");
const micro = require("micro");
const https = require("https");
const {json, send} = micro;
const config = require("./av.config");

const server = micro(async (req, res) => {
    let uwu = json(req);

    let vtRes = await request("POST", `https://www.virustotal.com/vtapi/v2/url/report`, {}, JSON.stringify({resource: uwu.url, apikey: config.apiKey, scan: "1"}));

    if (vtRes !== "204") send(res, 429, JSON.stringify({code: "429", message: "Exceeded Virustotal ratelimit."}));
    else {

        // Scans the URL. We inform the front-facing REST if its safe or not.

        let data = JSON.parse(vtRes).body;

        if (data.scans.MalwarePatrol.detected !== "false") send(res, 451, JSON.stringify({code: "451", message: "Reported URL Malware. Delete immediately."}));

        else send(res, 200, JSON.stringify({code: "200", message: "URL Reported OK. No Malware found."}));
    }
});

server.listen(parseInt(config.port));

// simple request function for creating a Promisified HTTP/S request.
function request(method, url, options = {}, payload) {
    return new Promise((resolve, reject) => {
        let req = https.request(Object.assign(URL.parse(url), options, {method}), res => {
            let chunked = "";

            if (res.statusCode !== 200) return reject(new Error(`HTTP ${res.statusCode}: ${res.statusMessage}`));

            res.setEncoding("utf8");
            res.on("data", chunk => chunked += chunk);
            res.on("error", reject);
            res.on("end", () => {
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

        req.on("error", reject);
        if (payload) req.write(payload);
        req.end();
    });
}