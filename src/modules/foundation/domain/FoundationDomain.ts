import { Foundation } from '../types';

export class FoundationDomain {
  /**
   * Validates foundation data according to business rules.
   * @throws Error if validation fails.
   */
  static validate(data: Partial<Foundation>): boolean {
    if (!data.company_name) {
      throw new Error('Required field missing: company_name');
    }

    if (data.company_name.length > 100) {
      throw new Error('Company name too long (max 100 characters)');
    }

    if (data.mission && data.mission.length > 500) {
      throw new Error('Mission too long (max 500 characters)');
    }

    if (data.vision && data.vision.length > 500) {
      throw new Error('Vision too long (max 500 characters)');
    }

    if (data.values && !Array.isArray(data.values)) {
      throw new Error('values must be a list');
    }

    if (data.messaging_guardrails && !Array.isArray(data.messaging_guardrails)) {
      throw new Error('messaging_guardrails must be a list');
    }

    return true;
  }
}
