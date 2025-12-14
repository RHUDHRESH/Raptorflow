/**
 * Mailchimp Connector
 *
 * Integration with Mailchimp API for email marketing campaigns.
 */

import { BaseConnector, ConnectorConfig, ConnectorResult } from './interface';

export interface MailchimpAudience {
  id: string;
  name: string;
  member_count: number;
  campaign_defaults: {
    from_name: string;
    from_email: string;
    subject: string;
    language: string;
  };
}

export interface MailchimpCampaign {
  id: string;
  type: 'regular' | 'plaintext' | 'absplit' | 'rss' | 'automation';
  status: 'save' | 'paused' | 'schedule' | 'sending' | 'sent';
  settings: {
    subject_line: string;
    title: string;
    from_name: string;
    reply_to: string;
  };
  recipients: {
    list_id: string;
    segment_opts?: any;
  };
  content_type?: 'template' | 'html' | 'url';
}

export interface MailchimpTemplate {
  id: number;
  name: string;
  html: string;
  thumbnail: string;
  drag_and_drop: boolean;
}

export class MailchimpConnector extends BaseConnector {
  private baseUrl: string;

  constructor(config: ConnectorConfig) {
    super(config);

    if (!config.apiKey) {
      throw new Error('Mailchimp API key required');
    }

    // Extract data center from API key
    const dataCenter = config.apiKey.split('-')[1];
    this.baseUrl = `https://${dataCenter}.api.mailchimp.com/3.0`;
  }

  async testConnection(): Promise<ConnectorResult<boolean>> {
    try {
      await this.makeRequest('/ping');
      return {
        success: true,
        data: true,
      };
    } catch (error: any) {
      return {
        success: false,
        error: `Mailchimp connection failed: ${error.message}`,
      };
    }
  }

  async getAudiences(): Promise<ConnectorResult<MailchimpAudience[]>> {
    try {
      const response = await this.makeRequest('/lists?count=100');

      const audiences: MailchimpAudience[] = response.lists.map((list: any) => ({
        id: list.id,
        name: list.name,
        member_count: list.stats.member_count,
        campaign_defaults: list.campaign_defaults,
      }));

      return {
        success: true,
        data: audiences,
      };
    } catch (error: any) {
      return {
        success: false,
        error: `Failed to get audiences: ${error.message}`,
      };
    }
  }

  async createCampaign(campaign: Omit<MailchimpCampaign, 'id'>): Promise<ConnectorResult<string>> {
    try {
      const response = await this.makeRequest('/campaigns', {
        method: 'POST',
        body: JSON.stringify(campaign),
      });

      return {
        success: true,
        data: response.id,
      };
    } catch (error: any) {
      return {
        success: false,
        error: `Failed to create campaign: ${error.message}`,
      };
    }
  }

  async updateCampaignContent(campaignId: string, content: any): Promise<ConnectorResult<boolean>> {
    try {
      await this.makeRequest(`/campaigns/${campaignId}/content`, {
        method: 'PUT',
        body: JSON.stringify(content),
      });

      return {
        success: true,
        data: true,
      };
    } catch (error: any) {
      return {
        success: false,
        error: `Failed to update campaign content: ${error.message}`,
      };
    }
  }

  async sendCampaign(campaignId: string): Promise<ConnectorResult<boolean>> {
    try {
      await this.makeRequest(`/campaigns/${campaignId}/actions/send`, {
        method: 'POST',
      });

      return {
        success: true,
        data: true,
      };
    } catch (error: any) {
      return {
        success: false,
        error: `Failed to send campaign: ${error.message}`,
      };
    }
  }

  async getTemplates(): Promise<ConnectorResult<MailchimpTemplate[]>> {
    try {
      const response = await this.makeRequest('/templates?count=100&type=user');

      const templates: MailchimpTemplate[] = response.templates.map((template: any) => ({
        id: template.id,
        name: template.name,
        html: template.html || '',
        thumbnail: template.thumbnail || '',
        drag_and_drop: template.drag_and_drop || false,
      }));

      return {
        success: true,
        data: templates,
      };
    } catch (error: any) {
      return {
        success: false,
        error: `Failed to get templates: ${error.message}`,
      };
    }
  }

  getMetadata() {
    return {
      name: 'Mailchimp Email Marketing',
      description: 'Mailchimp API integration for email campaigns and automation',
      capabilities: [
        'create_campaign',
        'send_campaign',
        'manage_audiences',
        'email_templates',
        'automation_workflows',
        'analytics_reporting',
      ],
      rateLimits: {
        requests: 10000, // per day for most plans
        period: 86400000,
      },
      costPerRequest: 0, // Included in subscription
    };
  }

  private async makeRequest(endpoint: string, options: RequestInit = {}): Promise<any> {
    const url = `${this.baseUrl}${endpoint}`;

    const auth = Buffer.from(`any:${this.config.apiKey}`).toString('base64');

    const response = await fetch(url, {
      ...options,
      headers: {
        'Authorization': `Basic ${auth}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(`Mailchimp API error: ${response.status} - ${error.detail || error.title || response.statusText}`);
    }

    return response.json();
  }
}

// Stub implementation
export class MailchimpConnectorStub extends BaseConnector {
  private mockAudiences: MailchimpAudience[] = [
    {
      id: 'audience_1',
      name: 'Main Subscriber List',
      member_count: 12500,
      campaign_defaults: {
        from_name: 'Company Name',
        from_email: 'hello@company.com',
        subject: 'Newsletter',
        language: 'en',
      },
    },
  ];

  private mockCampaigns: MailchimpCampaign[] = [];

  async testConnection(): Promise<ConnectorResult<boolean>> {
    return {
      success: true,
      data: true,
    };
  }

  async getAudiences(): Promise<ConnectorResult<MailchimpAudience[]>> {
    console.log(`📧 [STUB] Retrieved ${this.mockAudiences.length} Mailchimp audiences`);

    return {
      success: true,
      data: [...this.mockAudiences],
    };
  }

  async createCampaign(campaign: Omit<MailchimpCampaign, 'id'>): Promise<ConnectorResult<string>> {
    const campaignId = `campaign_${Date.now()}`;
    const fullCampaign: MailchimpCampaign = {
      ...campaign,
      id: campaignId,
    };

    this.mockCampaigns.push(fullCampaign);

    console.log(`📧 [STUB] Created Mailchimp campaign: ${fullCampaign.settings.title}`);

    return {
      success: true,
      data: campaignId,
    };
  }

  async updateCampaignContent(campaignId: string, content: any): Promise<ConnectorResult<boolean>> {
    console.log(`📧 [STUB] Updated content for campaign: ${campaignId}`);

    return {
      success: true,
      data: true,
    };
  }

  async sendCampaign(campaignId: string): Promise<ConnectorResult<boolean>> {
    console.log(`📧 [STUB] Sent campaign: ${campaignId}`);

    return {
      success: true,
      data: true,
    };
  }

  async getTemplates(): Promise<ConnectorResult<MailchimpTemplate[]>> {
    const mockTemplates: MailchimpTemplate[] = [
      {
        id: 1,
        name: 'Welcome Email',
        html: '<html><body>Welcome!</body></html>',
        thumbnail: 'https://via.placeholder.com/200x150',
        drag_and_drop: true,
      },
    ];

    return {
      success: true,
      data: mockTemplates,
    };
  }

  getMetadata() {
    return {
      name: 'Mailchimp Email Marketing (Stub)',
      description: 'Stub implementation for development and testing',
      capabilities: ['create_campaign', 'send_campaign', 'manage_audiences'],
      rateLimits: {
        requests: 10000,
        period: 86400000,
      },
    };
  }
}

