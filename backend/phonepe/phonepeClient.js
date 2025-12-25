const { Env, StandardCheckoutClient } = require('pg-sdk-node');

const REQUIRED_ENV_VARS = [
  'PHONEPE_CLIENT_ID',
  'PHONEPE_CLIENT_SECRET',
  'PHONEPE_CLIENT_VERSION',
  'PHONEPE_ENV',
];

const getRequiredEnv = (name) => {
  const value = process.env[name];
  if (!value) {
    throw new Error(`PhonePe config error: missing ${name}.`);
  }
  return value;
};

const resolveEnv = () => {
  const envValue = getRequiredEnv('PHONEPE_ENV').toUpperCase();
  if (!(envValue in Env)) {
    throw new Error(
      `PhonePe config error: PHONEPE_ENV must be SANDBOX or PRODUCTION (got ${envValue}).`
    );
  }
  return Env[envValue];
};

const validateEnv = () => {
  REQUIRED_ENV_VARS.forEach((name) => getRequiredEnv(name));
  const clientVersion = Number(getRequiredEnv('PHONEPE_CLIENT_VERSION'));
  if (!Number.isFinite(clientVersion)) {
    throw new Error('PhonePe config error: PHONEPE_CLIENT_VERSION must be a number.');
  }
  resolveEnv();
  return clientVersion;
};

let client;

const getClient = () => {
  if (!client) {
    const clientId = getRequiredEnv('PHONEPE_CLIENT_ID');
    const clientSecret = getRequiredEnv('PHONEPE_CLIENT_SECRET');
    const clientVersion = validateEnv();
    const env = resolveEnv();

    client = StandardCheckoutClient.getInstance(
      clientId,
      clientSecret,
      clientVersion,
      env
    );
  }

  return client;
};

module.exports = {
  getClient,
};
