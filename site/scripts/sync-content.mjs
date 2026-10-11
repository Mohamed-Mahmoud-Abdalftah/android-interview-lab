import { cp, mkdir, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  cleanTitle,
  extractInterviewQuestion,
  rewriteCanonicalLinks,
  routeForCanonicalPath,
  stripFrontmatter,
  yamlScalar,
} from './content-core.mjs';

const siteRoot = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const academyRoot = path.dirname(siteRoot);
const docsRoot = path.join(siteRoot, 'src/content/docs');
const dataRoot = path.join(siteRoot, 'src/data');
const publicRoot = path.join(siteRoot, 'public');
const manifest = JSON.parse(await readFile(path.join(academyRoot, 'CONTENT-MANIFEST.json'), 'utf8'));

const generatedFolders = ['lessons', 'questions', 'answers', 'scenarios', 'labs', 'mocks', 'revision', 'speaking', 'reference'];
await Promise.all(generatedFolders.map((folder) => rm(path.join(docsRoot, folder), { recursive: true, force: true })));
await mkdir(dataRoot, { recursive: true });
await mkdir(path.join(publicRoot, 'data'), { recursive: true });

const canonicalFiles = new Set();
for (const item of manifest.items) {
  if (item.status !== 'reviewed') continue;
  if (item.path?.endsWith('.md')) canonicalFiles.add(item.path);
  if (item.answer_path?.endsWith('.md')) canonicalFiles.add(item.answer_path);
}

for (const folder of ['Flashcards-Revision', 'Speaking-Shadowing']) {
  const entries = await readdir(path.join(academyRoot, folder), { withFileTypes: true });
  for (const entry of entries) if (entry.isFile() && entry.name.endsWith('.md')) canonicalFiles.add(`${folder}/${entry.name}`);
}

for (const file of [
  'README.md',
  'START-HERE.md',
  'CONTINUE-HERE.md',
  'PROGRESS-TRACKER.md',
  'STUDY-SCHEDULE-48-DAYS.md',
  'ROADMAP.md',
  'COVERAGE-MATRIX.md',
  'PREREQUISITE-MAP.md',
  'SOURCE-REGISTER.md',
  'ISSUES-AND-LIMITATIONS.md',
  'FULL-GAP-AUDIT.md',
  'FILE-INVENTORY.md',
  'QUESTION-ALLOCATION.md',
  'EDITORIAL-TECHNICAL-REVIEW.md',
  'QUALITY-GATES.md',
  'BUILD-VERIFICATION.md',
  'RTL-STYLE-GUIDE.md',
  'templates/ARABIC-LESSON.md',
  'fixtures/RTL-MIXED-LANGUAGE.md',
  '09-Leadership-English/STAR-EVIDENCE-WORKSHEET.md',
  'projects/kotlin-jvm-labs/README.md',
  'docs/IMPLEMENTATION_AUDIT.md',
  'docs/CONTENT_GUIDELINES.md',
  'docs/ARCHITECTURE.md',
  'docs/DEPLOYMENT.md',
  'projects/CAPSTONE-ARCHITECTURE.md',
  'Interview-Question-Bank/BY-TOPIC.md',
  'Interview-Question-Bank/BY-DIFFICULTY.md',
  'Interview-Question-Bank/BY-INTERVIEW-STYLE.md',
]) {
  canonicalFiles.add(file);
}

const routeMap = {};
for (const canonicalPath of [...canonicalFiles].sort()) {
  const absolute = path.join(academyRoot, canonicalPath);
  const raw = await readFile(absolute, 'utf8');
  const { frontmatter, body: originalBody } = stripFrontmatter(raw);
  const route = routeForCanonicalPath(canonicalPath);
  const routeParts = route.split('/').filter(Boolean);
  const output = path.join(docsRoot, ...routeParts) + '.md';
  const id = yamlScalar(frontmatter, 'id') || path.basename(canonicalPath, '.md');
  const titleFromFrontmatter = yamlScalar(frontmatter, 'title');
  const titleFromBody = originalBody.match(/^#\s+(.+)$/m)?.[1] ?? id;
  const title = cleanTitle(titleFromFrontmatter || titleFromBody);
  const item = manifest.items.find((entry) => entry.path === canonicalPath || entry.answer_path === canonicalPath);
  const day = item?.day ?? '';
  let body = originalBody.replace(/^\s*#\s+.+\r?\n+/, '');
  body = rewriteCanonicalLinks(body, canonicalPath);
  const origin = canonicalPath.replaceAll('"', '&quot;');
  const lessonControl = item?.type === 'lesson' || item?.type === 'extended_topic'
    ? `\n<academy-progress lesson-id="${id}" lesson-title="${title}"></academy-progress>\n`
    : '';
  const generated = `---\ntitle: "${title}"\ndescription: "محتوى أكاديمية Android Interview Mastery — ${id}"\nsidebar:\n  label: "${id} — ${title}"\n  order: ${day || 999}\n---\n\n<div class="canonical-source"><bdi>${id}</bdi> · المصدر الأساسي: <code dir="ltr">${origin}</code></div>\n${lessonControl}\n${body.trim()}\n`;
  await mkdir(path.dirname(output), { recursive: true });
  await writeFile(output, generated, 'utf8');
  routeMap[canonicalPath] = route;
}

await rm(path.join(publicRoot, 'source'), { recursive: true, force: true });
for (const folder of ['projects/kotlin-jvm-labs/src/main', 'projects/kotlin-jvm-labs/src/test']) {
  await cp(path.join(academyRoot, folder), path.join(publicRoot, 'source', folder), { recursive: true });
}
await mkdir(path.join(publicRoot, 'source'), { recursive: true });
await cp(path.join(academyRoot, 'CONTENT-MANIFEST.json'), path.join(publicRoot, 'source/CONTENT-MANIFEST.json'));

const reviewed = manifest.items.filter((item) => item.status === 'reviewed');
const lessons = manifest.items.filter((item) => item.type === 'lesson').map((item) => ({
  id: item.id,
  title: item.title,
  day: item.day,
  status: item.status,
  route: item.status === 'reviewed' ? routeForCanonicalPath(item.path) : null,
  prerequisites: item.prerequisites ?? [],
}));
const questions = await Promise.all(reviewed.filter((item) => item.type === 'question').map(async (item) => {
  const raw = await readFile(path.join(academyRoot, item.path), 'utf8');
  const { frontmatter, body } = stripFrontmatter(raw);
  const question = extractInterviewQuestion(body);
  return {
    id: item.id,
    route: routeForCanonicalPath(item.path),
    answerRoute: routeForCanonicalPath(item.answer_path),
    lessonId: yamlScalar(frontmatter, 'lesson_id') || item.prerequisites?.[0] || '',
    topic: yamlScalar(frontmatter, 'topic'),
    difficulty: yamlScalar(frontmatter, 'difficulty'),
    style: yamlScalar(frontmatter, 'style'),
    expectedMinutes: Number(yamlScalar(frontmatter, 'expected_minutes')) || 3,
    category: item.id.split('-')[0],
    question,
  };
}));
const stats = {
  coreReviewed: lessons.filter((item) => item.status === 'reviewed').length,
  coreTotal: lessons.length,
  questions: questions.length,
  scenarios: reviewed.filter((item) => item.type === 'scenario').length,
  labs: reviewed.filter((item) => item.type === 'coding_challenge').length,
  specialists: reviewed.filter((item) => item.type === 'extended_topic').length,
  mocks: reviewed.filter((item) => item.type === 'mock_pack').length,
};
const academyData = { generatedAt: new Date().toISOString(), stats, lessons, questions, routeMap };
await writeFile(path.join(dataRoot, 'academy.json'), JSON.stringify(academyData, null, 2), 'utf8');
await writeFile(path.join(publicRoot, 'data/academy.json'), JSON.stringify(academyData), 'utf8');
console.log(`Synced ${canonicalFiles.size} canonical Markdown files; ${stats.coreReviewed}/${stats.coreTotal} core lessons ready.`);
await import('./sync-interview-lab.mjs');
