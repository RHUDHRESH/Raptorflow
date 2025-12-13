/**
 * SES Email Connector
 *
 * AWS SES integration for sending emails.
 */

import { SESClient, SendEmailCommand, SendTemplatedEmailCommand, VerifyEmailIdentityCommand } from '@aws-sdk/client-ses';
import { BaseConnector, ConnectorConfig, ConnectorResult } from './interface';

export interface EmailMessage {
  to: string[];
  cc?: string[];
  bcc?: string[];
  subject: string;
  body: {
    text?: string;
    html?: string;
  };
  from?: string;
  replyTo?: string;
  attachments?: Array<{
    filename: string;
    content: Buffer;
    contentType: string;
  }>;
}

export interface TemplateEmail {
  templateName: string;
  templateData: Record<string, any>;
  to: string[];
  from?: string;
}

export class SESConnector extends BaseConnector {
  private sesClient: SESClient;

  constructor(config: ConnectorConfig) {
    super(config);

    if (!config.apiKey && !config.accessToken) {
      throw new Error('AWS credentials required for SES connector');
    }

    this.sesClient = new SESClient({
      region: process.env.AWS_REGION || 'us-east-1',
      credentials: config.accessToken ? {
        accessKeyId: config.accessToken,
        secretAccessKey: config.apiSecret || '',
      } : undefined,
    });
  }

  async testConnection(): Promise<ConnectorResult<boolean>> {
    try {
      // Try to verify an email identity (this will fail but test connectivity)
      await this.sesClient.send(new VerifyEmailIdentityCommand({
        EmailAddress: 'test@example.com',
      }));

      return {
        success: true,
        data: true,
      };
    } catch (error: any) {
      // Expected to fail for test email, but connectivity works
      if (error.name === 'InvalidParameterValue') {
        return {
          success: true,
          data: true,
        };
      }

      return {
        success: false,
        error: `SES connection failed: ${error.message}`,
      };
    }
  }

  async sendEmail(message: EmailMessage): Promise<ConnectorResult<string>> {
    try {
      const command = new SendEmailCommand({
        Source: message.from || this.config.baseUrl, // Default from address
        Destination: {
          ToAddresses: message.to,
          CcAddresses: message.cc,
          BccAddresses: message.bcc,
        },
        Message: {
          Subject: {
            Data: message.subject,
            Charset: 'UTF-8',
          },
          Body: {
            Text: message.body.text ? {
              Data: message.body.text,
              Charset: 'UTF-8',
            } : undefined,
            Html: message.body.html ? {
              Data: message.body.html,
              Charset: 'UTF-8',
            } : undefined,
          },
        },
        ReplyToAddresses: message.replyTo ? [message.replyTo] : undefined,
      });

      const response = await this.sesClient.send(command);

      return {
        success: true,
        data: response.MessageId,
        metadata: {
          requestId: response.$metadata.requestId,
        },
      };
    } catch (error: any) {
      return {
        success: false,
        error: `Failed to send email: ${error.message}`,
      };
    }
  }

  async sendTemplatedEmail(templateEmail: TemplateEmail): Promise<ConnectorResult<string>> {
    try {
      const command = new SendTemplatedEmailCommand({
        Source: templateEmail.from || this.config.baseUrl,
        Template: templateEmail.templateName,
        TemplateData: JSON.stringify(templateEmail.templateData),
        Destination: {
          ToAddresses: templateEmail.to,
        },
      });

      const response = await this.sesClient.send(command);

      return {
        success: true,
        data: response.MessageId,
        metadata: {
          requestId: response.$metadata.requestId,
        },
      };
    } catch (error: any) {
      return {
        success: false,
        error: `Failed to send templated email: ${error.message}`,
      };
    }
  }

  getMetadata() {
    return {
      name: 'SES Email',
      description: 'AWS Simple Email Service for transactional and marketing emails',
      capabilities: [
        'send_email',
        'send_templated_email',
        'bulk_email',
        'email_tracking',
      ],
      rateLimits: {
        requests: 1000, // per second for sending
        period: 1000,
      },
      costPerRequest: 0.0001, // $0.10 per 1000 emails
    };
  }
}

// Stub implementation for development/testing
export class SESConnectorStub extends BaseConnector {
  private sentEmails: EmailMessage[] = [];

  async testConnection(): Promise<ConnectorResult<boolean>> {
    return {
      success: true,
      data: true,
    };
  }

  async sendEmail(message: EmailMessage): Promise<ConnectorResult<string>> {
    this.sentEmails.push(message);

    console.log(`📧 [STUB] Email sent to: ${message.to.join(', ')}`);
    console.log(`📧 [STUB] Subject: ${message.subject}`);

    return {
      success: true,
      data: `stub_message_${Date.now()}`,
      metadata: {
        requestId: `stub_${Date.now()}`,
      },
    };
  }

  async sendTemplatedEmail(templateEmail: TemplateEmail): Promise<ConnectorResult<string>> {
    console.log(`📧 [STUB] Templated email sent using: ${templateEmail.templateName}`);

    return {
      success: true,
      data: `stub_template_message_${Date.now()}`,
      metadata: {
        requestId: `stub_${Date.now()}`,
      },
    };
  }

  getMetadata() {
    return {
      name: 'SES Email (Stub)',
      description: 'Stub implementation for development and testing',
      capabilities: ['send_email', 'send_templated_email'],
      rateLimits: {
        requests: 1000,
        period: 1000,
      },
    };
  }

  getSentEmails(): EmailMessage[] {
    return [...this.sentEmails];
  }
}

