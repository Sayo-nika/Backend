/**
 * @file av_worker.js
 * @author Capuccino
 * @license BSD-3-Clause
 */
const got = require('got');
const micro = require("micro");
const {json, send} = micro;

const virusTotalURL = "https://www.virustotal.com/vtapi/v2/url/report";

exports.server = ({apiKey}) => micro(async (req, res) => {
    const reqBody = json(req);

    try {
        var avResponse = await got.get(virusTotalURL, {
            responseType: 'json',
            query: {
                resource: reqBody.url,
                apikey: apiKey,
                scan: 1
            }
        });
    } catch(err) {
        if (err instanceof got.HTTPError)
            send(res, 500, {
                statusCode: err.statusCode,
                message: err.statusMessage
            });
        else
            send(res, 500, {message: err.message});

        return;
    }

    if (avResponse.statusCode === 204) {
        send(res, 429);
        return;
    }

    const {body} = avResponse;

    if (body.response_code === 0 || body.response_code === -2) {
        send(res, 404, {message: "URL result not found or is in queue."});
        return;
    }

    if (!body.positives) send(res, 200, {ok: true});
    else {
        // Something had a positive, what though?
        const positives = Object.entries(body.scans)
            .filter(([, data]) => data.detected)
            .map(([service]) => service);

        send(res, 200, {ok: false, positives});
    }
});
