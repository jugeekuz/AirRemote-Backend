const readline = require("readline");
const fs = require("fs");
const { generateJWTSecret } = require('./createSecret');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

const message = `
==================================================================================
                           Welcome to Air Remote
==================================================================================
Version: 1.0
Developed by: Anastasios Diamantis

Initializing the application deployment...
==================================================================================

Instructions:
1. Update the \`config.json\` under the root directory with your own values before
deploying

2. This process will create a .env file in the /outputs directory. This file will 
   contain all the necessary endpoints for the frontend.
   - Make sure to replace the \`<CLIENT-ID>\` \`<COGNITO-DOMAIN>\` with your 
   values manually and place the .env file in the base directory of the frontend 
   project before deployment of the frontend project.

==================================================================================


Do you want to deploy? [Y/n]:`;

rl.question(message, (answer) => {
  const normalized = answer.trim().toLowerCase();
  
  if (normalized === 'n') {
    console.log('🚫 Deployment cancelled.');
    process.exit(1);
  }

  generateJWTSecret();
  console.log("🚀 Starting deployment process...");
  rl.close();
});
