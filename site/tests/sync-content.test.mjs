import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

import {
  extractInterviewQuestion,
  routeForCanonicalPath,
  rewriteCanonicalLinks,
  stripFrontmatter,
} from '../scripts/content-core.mjs';

test('maps canonical academy files to stable learner routes', () => {
  assert.equal(routeForCanonicalPath('01-Kotlin-JVM-ART/KOT-001-nullability-java-boundary.md'), '/lessons/kot-001/');
  assert.equal(routeForCanonicalPath('Interview-Question-Bank/Questions/KOT-Q001.md'), '/questions/kot-q001/');
  assert.equal(routeForCanonicalPath('Interview-Question-Bank/Model-Answers/KOT-Q001.md'), '/answers/kot-q001/');
  assert.equal(routeForCanonicalPath('Coding-Challenges/LAB-001-profile-name.md'), '/labs/lab-001/');
  assert.equal(routeForCanonicalPath('Mock-Interviews/mock-001-kotlin-and-coroutines.md'), '/mocks/mock-001-kotlin-and-coroutines/');
  assert.equal(routeForCanonicalPath('Mock-Interviews/README.md'), '/mocks/');
});

test('maps support material to dedicated reference routes', () => {
  assert.equal(routeForCanonicalPath('projects/kotlin-jvm-labs/README.md'), '/reference/jvm-lab/');
  assert.equal(routeForCanonicalPath('09-Leadership-English/STAR-EVIDENCE-WORKSHEET.md'), '/reference/star-evidence-worksheet/');
  assert.equal(routeForCanonicalPath('STUDY-SCHEDULE-48-DAYS.md'), '/reference/study-schedule-48-days/');
});

test('rewrites local markdown links relative to the canonical source file', () => {
  const source = '01-Kotlin-JVM-ART/KOT-001-nullability-java-boundary.md';
  const markdown = '[answer](../Interview-Question-Bank/Model-Answers/KOT-Q001.md)';
  assert.equal(rewriteCanonicalLinks(markdown, source), '[answer](/answers/kot-q001/)');
});

test('keeps external and anchor links unchanged', () => {
  const source = '01-Kotlin-JVM-ART/KOT-001-nullability-java-boundary.md';
  const markdown = '[official](https://kotlinlang.org/docs/null-safety.html) [section](#trace)';
  assert.equal(rewriteCanonicalLinks(markdown, source), markdown);
});

test('separates canonical frontmatter from the lesson body', () => {
  const result = stripFrontmatter('---\nid: KOT-001\ntitle: Demo\n---\n# Body\n');
  assert.match(result.frontmatter, /id: KOT-001/);
  assert.equal(result.body, '# Body\n');
});

test('extracts the spoken interviewer prompt instead of its markdown heading', () => {
  const body = `# ARC-Q016 — Hilt scopes

## Interview question

> **Interviewer:** A teammate wants every dependency to be a Singleton. Do you agree?

<p dir="rtl">context</p>

## Follow-ups

1. Why?`;
  assert.equal(
    extractInterviewQuestion(body),
    'A teammate wants every dependency to be a Singleton. Do you agree?',
  );
});

test('extracts the full prose prompt around a code sample', () => {
  const body = `# KOT-Q006 — val

Consider:

\`\`\`kotlin
val names = mutableListOf("Ada")
\`\`\`

What does val prevent, and what remains mutable?

[Open complete model answer](../answer.md)`;
  assert.equal(
    extractInterviewQuestion(body),
    'Consider: What does val prevent, and what remains mutable?',
  );
});

test('preserves Kotlin star projections and identifier underscores in prompts', () => {
  const body = `# Types

What is \`List<*>\`, and why does \`Int.MAX_VALUE\` differ from \`request_id\`?`;
  assert.equal(
    extractInterviewQuestion(body),
    'What is List<*>, and why does Int.MAX_VALUE differ from request_id?',
  );
});

test('does not treat the letter z as the end of an interview question', () => {
  const body = `# UI-Q019 — Deep-link entry

## Interview question

> **Interviewer:** Build the validation, authentication, authorization, and navigation flow. Explain LazyColumn virtualization and serialize state safely.

<p dir="rtl">السياق بالمصري.</p>`;
  assert.equal(
    extractInterviewQuestion(body),
    'Build the validation, authentication, authorization, and navigation flow. Explain LazyColumn virtualization and serialize state safely.',
  );
});

test('keeps the curated Must Know path complete and explainable', () => {
  const component = readFileSync(new URL('../src/components/QuestionExplorer.astro', import.meta.url), 'utf8');
  const academy = JSON.parse(readFileSync(new URL('../src/data/academy.json', import.meta.url), 'utf8'));
  const mustKnowBlock = component.split('const mustKnowIds = [', 2)[1].split('];', 1)[0];
  const focusBlock = component.split('const interviewFocus', 2)[1].split('};', 1)[0];
  const ids = [...mustKnowBlock.matchAll(/'([A-Z]+-Q\d{3})'/g)].map((match) => match[1]);
  const focusIds = new Set([...focusBlock.matchAll(/'([A-Z]+-Q\d{3})'\s*:/g)].map((match) => match[1]));
  const academyIds = new Set(academy.questions.map((question) => question.id));

  assert.equal(ids.length, 54);
  assert.equal(new Set(ids).size, ids.length);
  assert.deepEqual(ids.filter((id) => !academyIds.has(id)), []);
  assert.deepEqual(ids.filter((id) => !focusIds.has(id)), []);
});
