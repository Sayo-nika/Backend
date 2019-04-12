// Filter environment variables to those only starting with `SAYONIKA_`, and then remove that from them (like backend does).
const env = Object.entries(process.env)
    .filter(([key]) => key.startsWith("SAYONIKA_"))
    .map(([key, value]) => ({[key.slice("SAYONIKA_".length)]: value}))
    .reduce((prev, value) => ({...prev, ...value}));

module.exports = {
    proxy: {
        port: parseInt(env.MICROSERVICES_PORT || 9000)
    },
    av: {
        port: parseInt(env.AV_PORT || 2000),
        apiKey: env.AV_VIRUSTOTAL_APIKEY
    },
    expirer: {
        host: env.DB_HOST || "localhost",
        port: parseInt(env.DB_PORT || 5432),
        database: env.DB_NAME || "sayonika",
        user: env.DB_USER || "sayonika",
        password: env.DB_PASS || "sayonika"
    }
};
