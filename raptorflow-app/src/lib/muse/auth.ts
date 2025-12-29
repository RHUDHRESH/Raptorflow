import { supabase } from '@/lib/supabase';

const internalKey = process.env.RF_INTERNAL_KEY || '';
const defaultTenantId = process.env.DEFAULT_TENANT_ID || '';

export async function getMuseAuthHeaders(): Promise<
  | {
      headers: Record<string, string>;
      tenantId: string;
    }
  | null
> {
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (session?.access_token && session.user?.id) {
    return {
      headers: {
        Authorization: `Bearer ${session.access_token}`,
        'X-Tenant-ID': session.user.id,
      },
      tenantId: session.user.id,
    };
  }

  if (internalKey && defaultTenantId) {
    return {
      headers: {
        'X-RF-Internal-Key': internalKey,
        'X-Tenant-ID': defaultTenantId,
      },
      tenantId: defaultTenantId,
    };
  }

  return null;
}
