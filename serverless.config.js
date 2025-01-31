const config = require('./config.json');

module.exports = (serverless) => {
  const stage = serverless.options.stage || 'dev';
  return {
    ...config,
    configFilePath: './config.json',
    scriptable: {
      hooks: {
        'before:package:createDeploymentArtifacts': 'node ./scripts/predeploy.js',
        'after:deploy:deploy': `node ./scripts/createEnv.js ${stage}`
      }
    }
  };
};