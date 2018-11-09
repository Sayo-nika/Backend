module.exports = {
     host: '' || process.env.SAYONIKA_EMAIL_HOST || 3000,
     port: '' || process.env.SAYONIKA_EMAIL_PORT,
     auth: {
        user: '' || process.env.SAYONIKA_EMAIL_USER,
        password: '' || process.env.SAYONIKA_EMAIL_PASSWORD
     },
     redis: {
         host: '' || process.env.SAYONIKA_REDIS_HOST,
         password: '' || process.env.SAYONIKA_REDIS_PASSWORD
     }
}