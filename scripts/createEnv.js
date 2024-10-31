// scripts/writeEnv.js

const fs = require('fs');
const { execSync } = require('child_process');

(async () => {
  try {
    const stage = process.argv[2] || 'dev';

    const output = execSync('serverless info').toString();

    const regex = /((https?|wss):\/\/[a-zA-Z0-9.-]+)\//g;
    
    const matches = new Set([...output.matchAll(regex)].map(match => match[1]));
    const urls = Array.from(matches);  
    
    const envContent = `VITE_STAGE="${stage}"\n` + 
      urls
      .map((url) => url.includes('https') ? `VITE_BASE_URL="${url}"` : `VITE_WSS_URL="${url}"`)
      .join('\n');

    // Path to save the .env file
    const envPath = './outputs/.env';
    fs.writeFileSync(envPath, envContent);

    console.log(`.env file created at ${envPath}`);
  } catch (error) {
    console.error('Error generating .env file:', error);
  }
})();
