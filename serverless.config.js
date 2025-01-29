const config = require('./config.json');

module.exports = {
  ...config,
  configFilePath: './config.json',

  scriptable: {
    hooks: {
      'before:package:createDeploymentArtifacts': 'node ./scripts/predeploy.js',
      'after:deploy:deploy': 'node ./scripts/createEnv.js'
    }
  }
};