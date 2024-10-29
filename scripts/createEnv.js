// scripts/writeEnv.js

const fs = require('fs');
const { execSync } = require('child_process');

(async () => {
  try {
    const output = execSync('serverless info').toString();

    const regex = /((https?|wss):\/\/[a-zA-Z0-9.-]+)\//g;
    
    const matches = new Set([...output.matchAll(regex)].map(match => match[1]));
    const urls = Array.from(matches);  
    
    const envContent = urls
      .map((url, index) => url.includes('https') ? `BASE_URL="${url}"` : `WSS_URL="${url}"`)
      .join('\n');

    // Path to save the .env file
    const envPath = './outputs/.env';
    fs.writeFileSync(envPath, envContent);

    console.log(`.env file created at ${envPath}`);
  } catch (error) {
    console.error('Error generating .env file:', error);
  }
})();
