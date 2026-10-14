import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30_000,
  retries: 0,
  workers: 2,
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:4539/android-interview-lab/',
    browserName: 'chromium',
    channel: 'chrome',
    viewport: { width: 1280, height: 800 },
  },
  webServer: {
    command: 'python3 scripts/serve-subpath.py 2>/dev/null',
    url: 'http://127.0.0.1:4539/android-interview-lab/',
    reuseExistingServer: true,
    timeout: 60_000,
  },
});
