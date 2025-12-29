import { IcpCompanyType, IcpSalesMotion } from '@/types/icp-types';

/**
 * Returns a default sales motion based on the company type.
 * This is used to provide smart defaults in the ICP Wizard.
 *
 * @param companyType The company type selected by the user
 * @returns An array containing the default sales motion, or undefined if no default matches
 */
export function getDefaultSalesMotion(
  companyType: IcpCompanyType | undefined
): IcpSalesMotion[] | undefined {
  if (!companyType) return undefined;

  switch (companyType) {
    case 'saas':
      return ['demo-led'];
    case 'd2c':
      return ['self-serve'];
    case 'agency':
    case 'service':
      return ['sales-assisted'];
    default:
      return undefined;
  }
}
