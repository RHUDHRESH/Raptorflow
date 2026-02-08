import js from '@eslint/js';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import globals from 'globals';
import tsParser from '@typescript-eslint/parser';
import tsPlugin from '@typescript-eslint/eslint-plugin';

export default [
  {
    ignores: [
      'dist/**',
      'database/**',
      'node_modules/**',
      '.next/**',
      'coverage/**',
      'playwright-report/**',
    ],
  },
  js.configs.recommended,
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    languageOptions: {
      // Parse everything with the TS parser so we can lint TS/TSX without CLI flags.
      parser: tsParser,
      ecmaVersion: 2022,
      sourceType: 'module',
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        ...globals.browser,
        ...globals.es2022,
        ...globals.node,
      },
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
      react,
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
    rules: {
      // TypeScript handles undefined identifiers at compile-time; this rule is noisy with TS namespaces.
      'no-undef': 'off',
      ...react.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      'react/react-in-jsx-scope': 'off',
      'react/jsx-uses-react': 'off',
      'react-refresh/only-export-components': 'off',
      'react/no-unescaped-entities': 'off',
      // Next.js styled-jsx uses <style jsx global>, which this rule doesn't understand.
      'react/no-unknown-property': 'off',
      // TypeScript is the source of truth for component props.
      'react/prop-types': 'off',
      'react-hooks/exhaustive-deps': 'warn',
      // TypeScript-aware unused vars rule (instead of base `no-unused-vars`).
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': [
        'warn',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
    },
  },
  {
    files: [
      '**/__tests__/**/*.{js,jsx,ts,tsx}',
      '**/*.test.{js,jsx,ts,tsx}',
      '**/*.spec.{js,jsx,ts,tsx}',
    ],
    languageOptions: {
      globals: {
        ...globals.jest,
      },
    },
  },
];
