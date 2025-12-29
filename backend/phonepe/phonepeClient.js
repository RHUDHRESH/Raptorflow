const { Env, StandardCheckoutClient } = require('pg-sdk-node');

const ENV_ALIASES = {
  UAT: 'SANDBOX',
  TEST: 'SANDBOX',
};

const getOptionalEnv = (name) => {
  const value = process.env[name];
  return value ? String(value).trim() : '';
};

const getRequiredEnv = (name) => {
  const value = getOptionalEnv(name);
  if (!value) {
    throw new Error(`PhonePe config error: missing ${name}.`);
  }
  return value;
};

const resolveEnv = () => {
  const envValue = getRequiredEnv('PHONEPE_ENV').toUpperCase();
  const resolved = ENV_ALIASES[envValue] || envValue;
  if (!(resolved in Env)) {
    throw new Error(
      `PhonePe config error: PHONEPE_ENV must be SANDBOX or PRODUCTION (got ${envValue}).`
    );
  }
  return Env[resolved];
};

const parseNumber = (raw, label) => {
  const value = Number(raw);
  if (!Number.isFinite(value)) {
    throw new Error(`PhonePe config error: ${label} must be a number.`);
  }
  return value;
};

let client;

const getClient = () => {
  if (client) {
    return client;
  }

  const env = resolveEnv();
  const clientId = getOptionalEnv('PHONEPE_CLIENT_ID');
  const clientSecret = getOptionalEnv('PHONEPE_CLIENT_SECRET');
  const merchantId = getOptionalEnv('PHONEPE_MERCHANT_ID');
  const saltKey = getOptionalEnv('PHONEPE_SALT_KEY');
  const saltIndex = getOptionalEnv('PHONEPE_SALT_INDEX');

  if (clientId && clientSecret) {
    const clientVersion = parseNumber(
      getRequiredEnv('PHONEPE_CLIENT_VERSION'),
      'PHONEPE_CLIENT_VERSION'
    );
    client = StandardCheckoutClient.getInstance(
      clientId,
      clientSecret,
      clientVersion,
      env
    );
    return client;
  }

  if (merchantId && saltKey) {
    const saltIndexValue = parseNumber(saltIndex || '1', 'PHONEPE_SALT_INDEX');
    client = StandardCheckoutClient.getInstance(
      merchantId,
      saltKey,
      saltIndexValue,
      env
    );
    return client;
  }

  throw new Error(
    'PhonePe config error: missing PHONEPE_CLIENT_ID/SECRET or PHONEPE_MERCHANT_ID/SALT_KEY.'
  );
};

module.exports = {
  getClient,
};
