import { apiRequest } from "@/services/http";

export type ContactRequest = {
  name: string;
  email: string;
  subject: string;
  message: string;
  source?: string;
  workspace_id?: string;
  metadata?: Record<string, unknown>;
};

export type ContactResponse = {
  accepted: boolean;
  status: string;
  support_delivery: string;
  ack_delivery: string;
};

export const communicationsService = {
  async sendContact(payload: ContactRequest): Promise<ContactResponse> {
    return apiRequest<ContactResponse>("/communications/contact", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};

