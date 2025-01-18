const readline = require("readline");
const fs = require("fs");
const { generateJWTSecret } = require('./createSecret');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

let corsOrigin = 'https://air-remote.pro';

const message = `
==================================================================================
                           Welcome to Air Remote
==================================================================================
Version: 1.0
Developed by: Anastasios Diamantis

Initializing the application deployment...
==================================================================================

Instructions:
1. This process will create a .env file in the /outputs directory. This file will 
   contain all the necessary endpoints for the frontend.
   - Make sure to place the .env file in the base directory of the frontend project 
     before deployment.

2. If you have the frontend URL, please include it in the next prompt to configure 
   CORS for the application. 
   - If you do not have the frontend URL yet, you can proceed with the deployment of 
     this app first, then deploy the frontend. After obtaining the frontend URL, 
     you can redeploy this app to set it as an origin server.

==================================================================================


Do you have the frontend URL? [Y/n]:`;

rl.question(message, (answer) => {
  if (answer.toLowerCase() === "n") {
    
    generateJWTSecret();

    const config = { corsOrigin };
    const filePath = "./config.json";
    fs.writeFileSync(filePath, JSON.stringify(config, null, 2));
    console.log("Config saved:", config);
    
    console.log("Continuing with deployment process, redeploy when you obtained the URL origin.");
    rl.close();
  } else {
    rl.question("Enter the frontend URL: ", (answer) => {
      corsOrigin = answer;
      // Write corsOrigin to a JSON file that serverless.yml can read
      const config = { corsOrigin };
      const filePath = "./config.json";
      fs.writeFileSync(filePath, JSON.stringify(config, null, 2));
      console.log("Config saved:", config);

      rl.close();
    });
  }
});
