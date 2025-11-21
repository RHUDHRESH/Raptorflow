# Validation and Sanitization Tests

This directory contains comprehensive test suites for the validation and sanitization utilities.

## Test Files

- `validation.test.js` - Tests for email, password, username, and field validation
- `sanitize.test.js` - Tests for XSS prevention and input sanitization

## Running Tests

First, install the testing dependencies:

```bash
npm install
```

Then run the tests:

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm run test:coverage

# Run tests with UI
npm run test:ui
```

## Test Coverage

The test suites cover:

### Validation Tests (validation.test.js)
- ✅ Email validation (format, length, special cases)
- ✅ Password validation (strength, length, character requirements)
- ✅ Username validation (format, length, allowed characters)
- ✅ Required field validation
- ✅ Length validation (min/max)
- ✅ Match validation (password confirmation)
- ✅ Edge cases and error handling

### Sanitization Tests (sanitize.test.js)
- ✅ HTML tag stripping
- ✅ XSS attack prevention (11+ attack vectors)
- ✅ Safe HTML allowlist
- ✅ Object sanitization (nested, arrays)
- ✅ Email sanitization
- ✅ Secure localStorage operations
- ✅ Performance and edge cases
- ✅ Circular reference handling

## Adding New Tests

When adding new validation or sanitization functions:

1. Add the function to the appropriate file (`validation.js` or `sanitize.js`)
2. Import it in the corresponding test file
3. Add test cases covering:
   - Happy path (valid inputs)
   - Error cases (invalid inputs)
   - Edge cases (empty, null, undefined, very long strings)
   - Security cases (XSS, injection attempts)

## Test Structure

Each test file follows this structure:

```javascript
describe('Feature Name', () => {
  it('should do something specific', () => {
    const result = functionToTest(input);
    expect(result).toBe(expectedOutput);
  });
});
```

## Dependencies

- **vitest** - Fast unit test framework
- **@testing-library/react** - React component testing utilities
- **@testing-library/jest-dom** - Custom matchers for DOM nodes
- **jsdom** - JavaScript implementation of web standards

## Continuous Integration

These tests should be run as part of your CI/CD pipeline to ensure code quality and security.
