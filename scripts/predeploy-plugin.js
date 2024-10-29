const { execSync } = require("child_process");

class PreDeployPlugin {
  constructor(serverless, options) {
    this.serverless = serverless;
    this.options = options;
    this.hooks = {
      "before:deploy:deploy": this.runPreDeployScript.bind(this),
    };
  }

  runPreDeployScript() {
    try {
      execSync("node ./scripts/predeploy.js", { stdio: "inherit" });
    } catch (error) {
      this.serverless.cli.log("Pre-deployment script failed:", error);
    }
  }
}

module.exports = PreDeployPlugin;
