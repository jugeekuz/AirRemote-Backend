const fs = require('fs');
const crypto = require('crypto');
require('dotenv').config();

function generateJWTSecret() {
    secret = crypto.randomBytes(32).toString('hex');

    const envContent = `JWT_SECRET=${secret}\n`;
    fs.writeFileSync('.env', envContent, { encoding: 'utf8' });
    console.log('Creating .env file with JWT_SECRET...');
}

module.exports = { generateJWTSecret };