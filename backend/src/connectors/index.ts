/**
 * Connectors Index
 *
 * Central exports for all external service connectors.
 */

// Base interface
export { BaseConnector } from './interface';
export type { ConnectorConfig, ConnectorResult } from './interface';

// SES Email connector
export { SESConnector, SESConnectorStub } from './ses';
export type { EmailMessage, TemplateEmail } from './ses';

// Figma connector
export { FigmaConnector, FigmaConnectorStub } from './figma';
export type { FigmaFile, FigmaImage, FigmaComment } from './figma';

// Mailchimp connector
export { MailchimpConnector, MailchimpConnectorStub } from './mailchimp';
export type { MailchimpAudience, MailchimpCampaign, MailchimpTemplate } from './mailchimp';

// Google Drive connector
export { GoogleDriveConnector, GoogleDriveConnectorStub } from './drive';
export type { DriveFile, DriveFolder } from './drive';

// Registry of available connectors
export const connectorRegistry = {
  // Real implementations
  SES: SESConnector,
  Figma: FigmaConnector,
  Mailchimp: MailchimpConnector,
  GoogleDrive: GoogleDriveConnector,

  // Stub implementations for development
  SESStub: SESConnectorStub,
  FigmaStub: FigmaConnectorStub,
  MailchimpStub: MailchimpConnectorStub,
  GoogleDriveStub: GoogleDriveConnectorStub,
} as const;

export type ConnectorName = keyof typeof connectorRegistry;

/**
 * Create a connector instance
 */
export function createConnector(name: ConnectorName, config: ConnectorConfig) {
  const ConnectorClass = connectorRegistry[name];
  return new ConnectorClass(config);
}

/**
 * Get connector metadata
 */
export function getConnectorMetadata(name: ConnectorName) {
  const instance = new connectorRegistry[name]({});
  return instance.getMetadata();
}

