// Shared token storage for testing
// In production, replace with database storage

const resetTokens = new Map<string, { email: string; expires: number }>();

export function storeToken(token: string, email: string, expires: number) {
  resetTokens.set(token, { email, expires });
}

export function getToken(token: string) {
  return resetTokens.get(token);
}

export function deleteToken(token: string) {
  return resetTokens.delete(token);
}

export function cleanupExpiredTokens() {
  const now = Date.now();
  for (const [token, data] of resetTokens.entries()) {
    if (data.expires < now) {
      resetTokens.delete(token);
    }
  }
}

// Auto-cleanup every 5 minutes
setInterval(cleanupExpiredTokens, 5 * 60 * 1000);
