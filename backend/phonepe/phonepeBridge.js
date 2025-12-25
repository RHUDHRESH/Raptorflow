const fs = require('fs');
const { StandardCheckoutPayRequest } = require('pg-sdk-node');
const { getClient } = require('./phonepeClient');

const readInput = () => {
  const raw = fs.readFileSync(0, 'utf8');
  if (!raw) {
    return {};
  }
  return JSON.parse(raw);
};

const writeOutput = (data) => {
  process.stdout.write(JSON.stringify(data));
};

const fail = (error) => {
  const message = error instanceof Error ? error.message : String(error);
  process.stderr.write(message);
  process.exit(1);
};

const handlePay = async (payload) => {
  const request = StandardCheckoutPayRequest.builder()
    .merchantOrderId(payload.merchantOrderId)
    .amount(payload.amount)
    .redirectUrl(payload.redirectUrl)
    .build();

  const response = await getClient().pay(request);

  return {
    redirectUrl: response.redirectUrl,
    orderId: response.orderId,
    state: response.state,
    expireAt: response.expireAt,
  };
};

const handleStatus = async (payload) => {
  return getClient().getOrderStatus(payload.merchantOrderId);
};

const handleValidate = async (payload) => {
  return getClient().validateCallback(
    payload.username,
    payload.password,
    payload.authorization,
    payload.responseBody
  );
};

const main = async () => {
  const action = process.argv[2];
  const payload = readInput();

  if (!action) {
    throw new Error('PhonePe bridge error: missing action.');
  }

  switch (action) {
    case 'pay':
      return handlePay(payload);
    case 'status':
      return handleStatus(payload);
    case 'validate':
      return handleValidate(payload);
    default:
      throw new Error(`PhonePe bridge error: unknown action ${action}.`);
  }
};

main()
  .then(writeOutput)
  .catch(fail);
