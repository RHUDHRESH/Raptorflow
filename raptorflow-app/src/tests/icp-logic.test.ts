import { describe, it, expect } from 'vitest';
import { getDefaultSalesMotion } from '../lib/icp-logic';
import { IcpCompanyType } from '../types/icp-types';

describe('getDefaultSalesMotion', () => {
    it('should return ["demo-led"] for "saas"', () => {
        const result = getDefaultSalesMotion('saas');
        expect(result).toEqual(['demo-led']);
    });

    it('should return ["self-serve"] for "d2c"', () => {
        const result = getDefaultSalesMotion('d2c');
        expect(result).toEqual(['self-serve']);
    });

    it('should return ["sales-assisted"] for "agency"', () => {
        const result = getDefaultSalesMotion('agency');
        expect(result).toEqual(['sales-assisted']);
    });

    it('should return ["sales-assisted"] for "service"', () => {
        const result = getDefaultSalesMotion('service');
        expect(result).toEqual(['sales-assisted']);
    });

    it('should return undefined for undefined input', () => {
        const result = getDefaultSalesMotion(undefined);
        expect(result).toBeUndefined();
    });

    // TypeScript ensures we pass valid IcpCompanyType, but at runtime:
    it('should return undefined for unknown types (if casted)', () => {
        const result = getDefaultSalesMotion('unknown' as IcpCompanyType);
        expect(result).toBeUndefined();
    });
});
