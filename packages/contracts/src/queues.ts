export const queueNames = {
  embedding: "embedding",
  contentPregeneration: "content-pregeneration",
  researchRequest: "research-request",
  internTask: "intern-task",
  toolGateway: "tool-gateway",
  eventHarvester: "event-harvester"
} as const;

export interface QueueEnvelope<TPayload> {
  jobType: string;
  payload: TPayload;
}
