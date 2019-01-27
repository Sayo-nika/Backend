/**
 * @file server.js
 * @description micro-proxy Proxy to handle routing for microservices.
 * @author Capuccino
 */

const createProxy = require("micro-proxy");
const config = require("./proxy.config");
const proxy = createProxy([
    // Proxy to email verification service
    {pathname: "/verify", method: ["POST", "OPTIONS"], dest: "http://localhost:4000"},
    // Proxy to email verification token sendmail service
    {pathname: "/sendmail", method: ["POST", "OPTIONS"], dest: "http://localhost:3000"},
    // Proxy to VirusTotal service
    {pathname: "/analyze", method: ["POST", "OPTIONS"], dest: "http://localhost:2000"}
]);

// call the loader before initing the port
require("./loader");

proxy.listen(parseInt(config.port), err => {
    if (err) {
        throw err;
    }
    console.log(`Microservices Proxy ready in port ${config.port}`);
});
