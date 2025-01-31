// scripts/writeEnv.js

const fs = require('fs');
const { execSync } = require('child_process');

const configPath = "./config.json";

const createAdmin = async (stage) => {

  if (!fs.existsSync(configPath)) {
    console.error("Error: config.json not found!");
    process.exit(1);
  }

  const config = JSON.parse(fs.readFileSync(configPath, "utf-8"));
  const { adminEmail, region } = config;
  const tableName = `${stage}RegisteredUsers`;

  if (!tableName) {
    console.error("❌ Error: REGISTERED_USERS_TABLE_NAME is not set.");
    process.exit(1);
  }
  console.log(`🛠️  Adding admin "${adminEmail}" to table "${tableName}" in region "${region}"...`);
  const command = `aws dynamodb put-item --table-name "${tableName}" --item "{\\"userEmail\\": {\\"S\\": \\"${adminEmail}\\"}}" --region "${region}"`;
  try {
    const output = execSync(command, { encoding: "utf-8" });
    console.log(`✅ Successfully added admin ${adminEmail} to registered users ${output}`);
  } catch (error) {
    console.error(`Error while creating admin: ${error.message}`);
  }
}


(async () => {
  try {
    const stage = process.argv[2] || 'dev'; 
    // const output = execSync(`serverless info --stage ${stage}`).toString();
    // const regex = /((https?|wss):\/\/[a-zA-Z0-9.-]+)\//g;
    // const matches = new Set([...output.matchAll(regex)].map(match => match[1]));
    // const urls = Array.from(matches);

    if (!fs.existsSync(configPath)) {
      console.error("Error: config.json not found!");
      process.exit(1);
    }
  
    const config = JSON.parse(fs.readFileSync(configPath, "utf-8"));
    const { corsOrigin } = config;
    const url = new URL(corsOrigin);
    const domain = url.hostname;
    
    const envContent = 
      `VITE_APP_CLIENT_ID="<YOUR-APP-CLIENT-ID>"\n` +
      `VITE_COGNITO_DOMAIN="<YOUR-COGNITO-DOMAIN>"\n` +
      `VITE_STAGE="${stage}"\n` +
      `VITE_BASE_URL="${corsOrigin}"\n` +
      `VITE_API_URL="https://api.${domain}/api"\n` +
      `VITE_AUTH_URL="https://auth.${domain}/auth"\n` +
      `VITE_WSS_URL="wss://wss.${domain}"\n`;



    // const envContent = `VITE_STAGE="${stage}"\nVITE_APP_CLIENT_ID="<YOUR-APP-CLIENT-ID>"\nVITE_COGNITO_DOMAIN="<YOUR-COGNITO-DOMAIN>"\n` + 
    //   urls
    //     .map((url) => url.includes('https') ? `VITE_BASE_URL="${url}"\nVITE_API_URL="${url}/api"\nVITE_AUTH_URL="${url}/auth"` : `VITE_WSS_URL="${url}"\n`)
    //     .join('\n');

    const envDir = './outputs';
    const envPath = './outputs/.env';
    
    if (!fs.existsSync(envDir)) {
      fs.mkdirSync(envDir, { recursive: true });
    }
    fs.writeFileSync(envPath, envContent);

    console.log(`.env file created at ${envPath}`);
    await createAdmin(stage);
  } catch (error) {
    console.error('Error generating .env file:', error);
  }
})();
