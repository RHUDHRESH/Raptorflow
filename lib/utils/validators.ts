export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function isStrongPassword(password: string): boolean {
  // At least 8 characters, one uppercase, one lowercase, one number
  return (
    password.length >= 8 &&
    /[A-Z]/.test(password) &&
    /[a-z]/.test(password) &&
    /[0-9]/.test(password)
  );
}

export function validateCampaignTitle(title: string): { valid: boolean; error?: string } {
  if (!title.trim()) return { valid: false, error: "Title is required" };
  if (title.length < 3) return { valid: false, error: "Title must be at least 3 characters" };
  if (title.length > 100) return { valid: false, error: "Title must be less than 100 characters" };
  return { valid: true };
}

export function validateMoveTitle(title: string): { valid: boolean; error?: string } {
  if (!title.trim()) return { valid: false, error: "Move title is required" };
  if (title.length < 3) return { valid: false, error: "Move title must be at least 3 characters" };
  if (title.length > 100) return { valid: false, error: "Move title must be less than 100 characters" };
  return { valid: true };
}
