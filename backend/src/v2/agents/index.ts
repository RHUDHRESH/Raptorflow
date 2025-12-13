/**
 * Agents Index
 *
 * Central exports for all orchestrator agents.
 */

// Base classes and types
export { BaseOrchestratorAgent } from './base';
export type { AgentManifest, AgentInput, AgentOutput, AgentContext } from './base';

// Individual agents
export { brandScriptAgent, brandScriptManifest } from './brandScript';
export { taglineAgent, taglineManifest } from './tagline';
export { productDescriptionAgent, productDescriptionManifest } from './productDescription';
export { oneLinerAgent, oneLinerManifest } from './oneLiner';
export { socialMediaIdeasAgent, socialMediaIdeasManifest } from './socialMediaIdeas';
export { salesEmailAgent, salesEmailManifest } from './salesEmail';
export { websiteWireframeAgent, websiteWireframeManifest } from './websiteWireframe';
export { productNameAgent, productNameManifest } from './productName';
export { packagingCopyAgent, packagingCopyManifest } from './packagingCopy';
export { leadGeneratorIdeasAgent, leadGeneratorIdeasManifest } from './leadGeneratorIdeas';
export { pdfGeneratorAgent, pdfGeneratorManifest } from './pdfGenerator';
export { domainSuggestionsAgent, domainSuggestionsManifest } from './domainSuggestions';
export { salesTalkingPointsAgent, salesTalkingPointsManifest } from './salesTalkingPoints';
export { videoScriptsAgent, videoScriptsManifest } from './videoScripts';
export { brandStoryAgent, brandStoryManifest } from './brandStory';
export { nurtureEmailsAgent, nurtureEmailsManifest } from './nurtureEmails';
export { imageGeneratorAgent } from './imageGenerator';

// Registry of all agents
export const agentRegistry = {
  BrandScript: brandScriptAgent,
  Tagline: taglineAgent,
  ProductDescription: productDescriptionAgent,
  OneLiner: oneLinerAgent,
  SocialMediaIdeas: socialMediaIdeasAgent,
  SalesEmail: salesEmailAgent,
  WebsiteWireframe: websiteWireframeAgent,
  ProductName: productNameAgent,
  PackagingCopy: packagingCopyAgent,
  LeadGeneratorIdeas: leadGeneratorIdeasAgent,
  PDFGenerator: pdfGeneratorAgent,
  DomainSuggestions: domainSuggestionsAgent,
  SalesTalkingPoints: salesTalkingPointsAgent,
  VideoScripts: videoScriptsAgent,
  BrandStory: brandStoryAgent,
  NurtureEmails: nurtureEmailsAgent,
  ImageGenerator: imageGeneratorAgent,
} as const;

export type AgentName = keyof typeof agentRegistry;
