import { devices, defineConfig } from "@playwright/test";

const authStatePath = "./playwright/.clerk/user.json";

if (typeof process.loadEnvFile === "function") {
  process.loadEnvFile("../../.env");
  process.loadEnvFile(".env.local");
}

export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 30_000,
  fullyParallel: false,
  use: {
    baseURL: "http://localhost:3000",
    headless: true,
  },
  projects: [
    {
      name: "setup",
      testMatch: /global\.setup\.ts/,
      use: {
        ...devices["Desktop Chrome"],
      },
    },
    {
      name: "chromium",
      testIgnore: /global\.setup\.ts/,
      use: {
        ...devices["Desktop Chrome"],
        storageState: authStatePath,
      },
      dependencies: ["setup"],
    },
  ],
});
