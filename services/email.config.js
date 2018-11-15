module.exports = {
     host: '' || process.env.SAYONIKA_EMAIL_HOST,
     port: process.env.SAYONIKA_EMAIL_PORT || 3000,
     auth: {
        user: '' || process.env.SAYONIKA_EMAIL_USER,
        password: '' || process.env.SAYONIKA_EMAIL_PASSWORD
     },
     redis: {
         host: '' || process.env.SAYONIKA_REDIS_HOST,
         password: '' || process.env.SAYONIKA_REDIS_PASSWORD
     }
}