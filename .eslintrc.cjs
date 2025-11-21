module.exports = {
  root: true,
  env: {
    browser: true,
    es2022: true,
    node: true,
  },
  extends: [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
  ],
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: "module",
    ecmaFeatures: {
      jsx: true,
    },
  },
  settings: {
    react: {
      version: "detect",
    },
  },
  plugins: ["react-refresh"],
  rules: {
    "react/react-in-jsx-scope": "off",
    "react/jsx-uses-react": "off",
    "react-refresh/only-export-components": "off",
    "react/prop-types": "off",
    "react/no-unescaped-entities": "off",
    "react-hooks/exhaustive-deps": "off",
    "no-unused-vars": "off",
  },
  ignorePatterns: [
    "dist",
    "database",
  ],
  overrides: [
    {
      files: ["**/__tests__/**/*.{js,jsx}", "**/*.test.{js,jsx}"],
      env: {
        jest: true,
      },
    },
  ],
};
