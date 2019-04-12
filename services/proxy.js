/**
 * @file micro-proxy Proxy to handle routing for microservices.
 * @author Capuccino
 */

const createProxy = require("micro-proxy");
const config = require("./config");
const av = require("./virus-checks");
const expirer = require('./account-expirer');

const proxy = createProxy([
    // Anti-virus file checking.
    {
        pathname: "/analyze",
        method: ["POST", "OPTIONS"],
        dest: `http://localhost:${config.av.port}`
    }
]);

expirer(config.expirer);
av(config.av).listen(config.av.port);

proxy.listen(config.proxy.port, err => {
    if (err) throw err;

    console.log(`Microservices proxy ready in port ${config.proxy.port}`);
});
