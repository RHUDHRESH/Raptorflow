import { BedrockRuntimeClient, ConverseCommand } from "@aws-sdk/client-bedrock-runtime";

const MODEL_STRATEGIST =
  process.env.BEDROCK_MODEL_STRATEGIST ?? "mistral.mistral-large-3-675b-instruct";
const MODEL_FAST = process.env.BEDROCK_MODEL_FAST ?? "mistral.ministral-3-8b-instruct";
const AWS_REGION = process.env.AWS_REGION ?? "ap-south-1";

let _client: BedrockRuntimeClient | null = null;

function getClient(): BedrockRuntimeClient {
  if (!_client) {
    _client = new BedrockRuntimeClient({
      region: AWS_REGION,
      credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID ?? "",
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY ?? "",
      },
    });
  }
  return _client;
}

export async function converseStrategist(prompt: string, maxTokens: number): Promise<string> {
  const client = getClient();
  const command = new ConverseCommand({
    modelId: MODEL_STRATEGIST,
    messages: [
      {
        role: "user",
        content: [{ text: prompt }],
      },
    ],
    inferenceConfig: {
      maxTokens,
      temperature: 0.7,
      topP: 0.95,
    },
  });

  const response = await client.send(command);

  const text = response.output?.message?.content?.[0]?.text;
  if (!text) {
    throw new Error("Bedrock returned no text content");
  }
  return text;
}

export async function convergeFast(prompt: string, maxTokens: number): Promise<string> {
  const client = getClient();
  const command = new ConverseCommand({
    modelId: MODEL_FAST,
    messages: [
      {
        role: "user",
        content: [{ text: prompt }],
      },
    ],
    inferenceConfig: {
      maxTokens,
      temperature: 0.5,
      topP: 0.85,
    },
  });

  const response = await client.send(command);

  const text = response.output?.message?.content?.[0]?.text;
  if (!text) {
    throw new Error("Bedrock returned no text content");
  }
  return text;
}
