/**
 * @file index.js
 * @description server.js microservice loader
 * @author Capuccino
 */
const fs = require('fs');
const configRegex = str => /[a-zA-Z]+\.config\.js/gi.test(str);

let files = fs.readdirSync(__dirname).filter(v => v !== 'index.js' && v.endsWith('.js') && !configRegex(v) && v !== 'server.js');

files.forEach(v => {
    require(`${__dirname}/${v}`);
    console.log(`Loaded ${v.slice(0, -3)}`);
});
