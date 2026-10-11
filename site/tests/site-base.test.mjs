import test from 'node:test';
import assert from 'node:assert/strict';
import { siteBase, href } from '../scripts/site-base.mjs';

test('GitHub user and project sites get correct bases', () => {
  const oldRepo = process.env.GITHUB_REPOSITORY;
  const oldBase = process.env.PUBLIC_SITE_BASE;
  try {
    delete process.env.PUBLIC_SITE_BASE;
    process.env.GITHUB_REPOSITORY = 'team/team.github.io';
    assert.equal(siteBase(), '/');
    process.env.GITHUB_REPOSITORY = 'team/interview-lab';
    assert.equal(siteBase(), '/interview-lab/');
    assert.equal(href('/lab/questions/kot-01/'), '/interview-lab/lab/questions/kot-01/');
    process.env.PUBLIC_SITE_BASE = '/custom/';
    assert.equal(siteBase(), '/custom/');
  } finally {
    if (oldRepo === undefined) delete process.env.GITHUB_REPOSITORY; else process.env.GITHUB_REPOSITORY = oldRepo;
    if (oldBase === undefined) delete process.env.PUBLIC_SITE_BASE; else process.env.PUBLIC_SITE_BASE = oldBase;
  }
});
