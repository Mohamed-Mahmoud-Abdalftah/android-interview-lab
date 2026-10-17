import { expect, test } from '@playwright/test';

const base = '/android-interview-lab/';

async function acceptDialogDuring(page, action, expectedMessage) {
  let message;
  await Promise.all([
    page.waitForEvent('dialog').then(async (dialog) => {
      message = dialog.message();
      await dialog.accept();
    }),
    action(),
  ]);
  expect(message).toContain(expectedMessage);
}

test.beforeEach(async ({ page }) => {
  await page.goto(base);
  await page.evaluate(() => localStorage.clear());
});

test('topic exploration, exact and Arabic search, deep link, and answer sections', async ({ page }) => {
  await page.goto(`${base}lab/explore/`);
  const explorer = page.locator('lab-explorer');
  await expect(explorer.getByText('485 total')).toBeVisible();
  await explorer.getByRole('searchbox', { name: 'Search canonical questions' }).fill('KOT-01');
  await expect(explorer.getByText('1 matching questions')).toBeVisible();
  await explorer.getByRole('link', { name: /KOT-01/ }).click();
  await expect(page).toHaveURL(/\/lab\/questions\/kot-01\/$/);
  await expect(page.getByText('What is Kotlin, and why is it popular in Android development?').first()).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Interview answer — deep senior' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Follow-up questions' })).toBeVisible();
  await page.goto(`${base}lab/explore/`);
  await explorer.getByRole('searchbox', { name: 'Search canonical questions' }).fill('لغة');
  await expect(explorer.getByText(/matching questions/)).toBeVisible();
  await expect(explorer.locator('.lab-result').first()).toBeVisible();
});

test('bookmark, progress, notes and spaced review persist across reload', async ({ page }) => {
  await page.goto(`${base}lab/questions/kot-01/`);
  const practice = page.locator('lab-question');
  await practice.getByRole('button', { name: 'Bookmark', exact: true }).click();
  await practice.getByRole('combobox', { name: 'Progress for KOT-01' }).selectOption('learning');
  await practice.getByRole('textbox', { name: 'Private note / your answer' }).fill('Test the Java nullability boundary.');
  await expect(practice.getByText('Saved locally')).toBeVisible();
  await practice.getByRole('button', { name: 'Good', exact: true }).click();
  await expect(practice.getByText(/Next review:/)).toBeVisible();
  await page.reload();
  await expect(practice.getByRole('button', { name: 'Remove bookmark' })).toHaveAttribute('aria-pressed', 'true');
  await expect(practice.getByRole('combobox', { name: 'Progress for KOT-01' })).toHaveValue('practicing');
  await expect(practice.getByRole('textbox', { name: 'Private note / your answer' })).toHaveValue('Test the Java nullability boundary.');
  await page.goto(`${base}lab/`);
  await expect(page.locator('lab-dashboard').getByText('1', { exact: true }).first()).toBeVisible();
});

test('mock session keeps answers hidden, resumes, reveals, and records recap', async ({ page }) => {
  await page.goto(`${base}lab/practice/`);
  const mock = page.locator('lab-practice');
  await mock.getByRole('combobox', { name: 'Interview topic' }).selectOption('KOT');
  await mock.getByRole('button', { name: 'Start interview' }).click();
  await expect(mock.getByRole('heading', { name: /Question 1 of/ })).toBeVisible();
  await expect(mock.getByRole('link', { name: 'Open question page' })).toHaveCount(0);
  await mock.getByRole('textbox', { name: 'Your answer' }).fill('A typed practice answer.');
  await page.reload();
  await expect(mock.getByRole('textbox', { name: 'Your answer' })).toHaveValue('A typed practice answer.');
  await expect(mock.getByRole('link', { name: 'Open question page' })).toHaveCount(0);
  await mock.getByRole('button', { name: 'Reveal source page' }).click();
  await expect(mock.getByRole('link', { name: 'Open question page' })).toBeVisible();
  await mock.getByRole('combobox', { name: 'Self rating' }).selectOption('good');
  await mock.getByRole('button', { name: 'End session' }).click();
  await expect(mock.getByText(/Session ended: 1 of/)).toBeVisible();
});

test('export, reset, and import restore local progress', async ({ page }) => {
  await page.goto(`${base}lab/questions/kot-01/`);
  await page.locator('lab-question').getByRole('button', { name: 'Bookmark', exact: true }).click();
  await page.goto(`${base}lab/`);
  const dashboard = page.locator('lab-dashboard');
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    dashboard.getByRole('button', { name: 'Export progress' }).click(),
  ]);
  expect(download.suggestedFilename()).toBe('android-interview-lab-progress.json');
  const filePath = await download.path();
  await acceptDialogDuring(page, () => dashboard.getByRole('button', { name: 'Reset Interview Lab progress' }).click(), 'Delete all Interview Lab notes');
  await page.goto(`${base}lab/questions/kot-01/`);
  await expect(page.locator('lab-question').getByRole('button', { name: 'Bookmark', exact: true })).toBeVisible();
  await page.goto(`${base}lab/`);
  await acceptDialogDuring(page, () => dashboard.locator('input[type="file"]').setInputFiles(filePath), 'Replace this browser');
  await page.goto(`${base}lab/questions/kot-01/`);
  await expect(page.locator('lab-question').getByRole('button', { name: 'Remove bookmark' })).toBeVisible();
});

test('mobile viewport rendering for both English LTR and Arabic RTL', async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 720 });
  // English page: LTR HTML, LTR code, no overflow
  await page.goto(`${base}lab/questions/kot-01/`);
  await expect(page.locator('html')).toHaveAttribute('dir', 'ltr');
  await expect(page.locator('html')).toHaveAttribute('lang', 'en');
  expect(await page.locator('pre').first().evaluate((node) => getComputedStyle(node).direction)).toBe('ltr');
  const enWidth = await page.evaluate(() => ({ body: document.documentElement.scrollWidth, viewport: innerWidth }));
  expect(enWidth.body).toBeLessThanOrEqual(enWidth.viewport + 1);

  // Arabic page: RTL HTML, LTR code, no overflow
  await page.goto(`${base}ar/lab/questions/kot-01/`);
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
  await expect(page.locator('html')).toHaveAttribute('lang', /^ar/);
  expect(await page.locator('pre').first().evaluate((node) => getComputedStyle(node).direction)).toBe('ltr');
  const arWidth = await page.evaluate(() => ({ body: document.documentElement.scrollWidth, viewport: innerWidth }));
  expect(arWidth.body).toBeLessThanOrEqual(arWidth.viewport + 1);

  await page.goto(`${base}ar/lab/questions/sec-01/`);
  const arabicProseWithCode = page.locator('.sl-markdown-content').locator('p:not([dir="ltr"]):has(code), li:has(code)').first();
  await expect(arabicProseWithCode).toBeVisible();
  expect(await arabicProseWithCode.evaluate((node) => getComputedStyle(node).direction)).toBe('rtl');
  const inlineCode = arabicProseWithCode.locator('code').first();
  expect(await inlineCode.evaluate((node) => getComputedStyle(node).direction)).toBe('ltr');
  const secWidth = await page.evaluate(() => ({ body: document.documentElement.scrollWidth, viewport: innerWidth }));
  expect(secWidth.body).toBeLessThanOrEqual(secWidth.viewport + 1);
});

test('bilingual language switching and shared progress persistence', async ({ page }) => {
  // 1. Start in English default
  await page.goto(`${base}lab/questions/kot-01/`);
  await expect(page.locator('html')).toHaveAttribute('lang', 'en');
  await expect(page.getByRole('heading', { name: 'Interview answer — deep senior' })).toBeVisible();

  const practiceEn = page.locator('lab-question');
  await practiceEn.getByRole('button', { name: 'Bookmark', exact: true }).click();
  await practiceEn.getByRole('textbox', { name: 'Private note / your answer' }).fill('Bilingual persistence test note.');
  await expect(practiceEn.getByText('Saved locally')).toBeVisible();

  // 2. Switch to Arabic using the REAL Starlight header language dropdown
  const langSelectEn = page.locator('starlight-lang-select select').first();
  await langSelectEn.selectOption({ label: 'العربية' });
  await expect(page).toHaveURL(/\/ar\/lab\/questions\/kot-01\/$/);
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
  await expect(page.locator('html')).toHaveAttribute('lang', /^ar/);
  await expect(page.getByRole('heading', { name: 'إجابة المقابلة — مناقشة Senior متعمقة' })).toBeVisible();

  // Verify full Arabic content rendering
  await expect(page.getByRole('heading', { name: 'ما يقيّمه المحاور' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'المفاضلات الهندسية ومعايير القرار' })).toBeVisible();

  // Verify progress is shared across language switch!
  const practiceAr = page.locator('lab-question');
  await expect(practiceAr.getByRole('button', { name: 'إزالة من المفضلة' })).toHaveAttribute('aria-pressed', 'true');
  await expect(practiceAr.getByRole('textbox', { name: 'ملاحظة خاصة / إجابتك الشخصية' })).toHaveValue('Bilingual persistence test note.');

  // 3. Switch back to English using the Arabic page's Starlight header language dropdown
  const langSelectAr = page.locator('starlight-lang-select select').first();
  await langSelectAr.selectOption({ label: 'English' });
  await expect(page).toHaveURL(/\/lab\/questions\/kot-01\/$/);
  await expect(page.locator('html')).toHaveAttribute('dir', 'ltr');
  await expect(page.locator('html')).toHaveAttribute('lang', 'en');
  await expect(page.getByRole('heading', { name: 'Interview answer — deep senior' })).toBeVisible();
  await expect(practiceEn.getByRole('button', { name: 'Remove bookmark' })).toHaveAttribute('aria-pressed', 'true');
  await expect(practiceEn.getByRole('textbox', { name: 'Private note / your answer' })).toHaveValue('Bilingual persistence test note.');
});

test('flashcard grades update schedule and explorer shows an empty state', async ({ page }) => {
  await page.goto(`${base}lab/review/`);
  const review = page.locator('lab-review');
  await expect(review.getByText('485 not yet reviewed')).toBeVisible();
  const first = review.locator('.lab-result').first();
  await first.getByRole('button', { name: 'good' }).click();
  await page.goto(`${base}lab/questions/kot-01/`);
  await expect(page.locator('lab-question').getByText(/Next review:/)).toBeVisible();
  await page.goto(`${base}lab/explore/`);
  const explorer = page.locator('lab-explorer');
  await explorer.getByRole('searchbox', { name: 'Search canonical questions' }).fill('no-such-question-999');
  await expect(explorer.getByText('No matching questions. Try a broader search or clear filters.')).toBeVisible();
});

test('invalid import does not change progress and missing routes return 404', async ({ page }) => {
  await page.goto(`${base}lab/questions/kot-01/`);
  await page.locator('lab-question').getByRole('button', { name: 'Bookmark', exact: true }).click();
  await page.goto(`${base}lab/`);
  const dashboard = page.locator('lab-dashboard');
  await acceptDialogDuring(page, () => dashboard.locator('input[type="file"]').setInputFiles({
    name: 'broken.json', mimeType: 'application/json', buffer: Buffer.from('{ broken json'),
  }), 'Invalid or unsupported progress JSON');
  await page.goto(`${base}lab/questions/kot-01/`);
  await expect(page.locator('lab-question').getByRole('button', { name: 'Remove bookmark' })).toBeVisible();
  const response = await page.goto(`${base}lab/questions/not-a-real-id/`);
  expect(response.status()).toBe(404);
});

test('a question opened once remains readable and interactive offline', async ({ browser }) => {
  const context = await browser.newContext({ serviceWorkers: 'allow' });
  const page = await context.newPage();
  try {
    await page.goto(`http://127.0.0.1:4539${base}lab/questions/kot-01/`);
    await page.evaluate(() => navigator.serviceWorker.ready);
    await page.waitForLoadState('networkidle');
    await context.setOffline(true);
    const response = await page.reload();
    expect(response?.status()).toBe(200);
    await expect(page.getByRole('heading', { name: 'Interview answer — deep senior' })).toBeVisible();
    const question = page.locator('lab-question');
    expect(parseFloat(await question.locator('.lab-tool').evaluate((node) => getComputedStyle(node).borderRadius))).toBeGreaterThan(0);
    await question.getByRole('button', { name: 'Bookmark', exact: true }).click();
    await page.reload();
    await expect(question.getByRole('button', { name: 'Remove bookmark' })).toBeVisible();
  } finally {
    await context.close();
  }
});
