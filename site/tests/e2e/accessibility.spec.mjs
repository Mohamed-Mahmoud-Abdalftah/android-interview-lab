import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';

for (const route of ['lab/', 'lab/explore/', 'lab/questions/kot-01/', 'lab/practice/']) {
  test(`WCAG A/AA on ${route}`, async ({ page }) => {
    await page.goto(`/android-interview-lab/${route}`);
    await expect(page.locator('main')).toBeVisible();
    const result = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();
    expect(result.violations.map(item => ({ id: item.id, nodes: item.nodes.map(n => n.target) }))).toEqual([]);
  });
}
