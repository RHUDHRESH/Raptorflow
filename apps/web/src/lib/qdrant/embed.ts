import { BedrockRuntimeClient, InvokeModelCommand } from "@aws-sdk/client-bedrock-runtime";

const AWS_REGION = process.env.AWS_REGION ?? "ap-south-1";
const EMBED_MODEL = "amazon.titan-embed-text-v2:0";

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

export async function embedText(text: string): Promise<number[]> {
  const client = getClient();
  const command = new InvokeModelCommand({
    modelId: EMBED_MODEL,
    contentType: "application/json",
    accept: "application/json",
    body: JSON.stringify({
      inputText: text,
      dimensions: 1536,
      normalize: true,
    }),
  });

  const response = await client.send(command);
  const body = JSON.parse(new TextDecoder().decode(response.body)) as {
    embedding?: number[];
    embeddings?: number[];
  };

  const vector = body.embedding ?? body.embeddings?.[0];
  if (!vector || !Array.isArray(vector)) {
    throw new Error("Bedrock embedding returned no vector");
  }
  return vector;
}
