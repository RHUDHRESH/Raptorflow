import { describe, test, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

describe('Foundation Module Structure', () => {
  const modulePath = path.resolve(__dirname, '..');

  test('should have required directories', () => {
    const directories = ['domain', 'services', 'types', '__tests__'];
    directories.forEach(dir => {
      const fullPath = path.join(modulePath, dir);
      expect(fs.existsSync(fullPath)).toBe(true);
      expect(fs.lstatSync(fullPath).isDirectory()).toBe(true);
    });
  });
});
