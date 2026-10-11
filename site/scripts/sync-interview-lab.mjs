import { mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { href } from './site-base.mjs';

const siteRoot = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const root = path.dirname(siteRoot);
const docs = path.join(siteRoot, 'src/content/docs/lab');
const manifest = JSON.parse(await readFile(path.join(root, 'reports/source-manifest.json'), 'utf8'));
const questions = manifest.questions;
const title = (value) => JSON.stringify(value);
const escapeHtml = (value) => value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const sourceOnly = [];
const reviewed = [];
const searchText = {};
const topicGuide = {
  KOT: ['Reason about Kotlin semantics before discussing framework behavior.', []],
  AND: ['Trace Activity, process, and Context lifetime before choosing a state owner.', ['KOT']],
  MEM: ['Diagnose leaks, ANRs, and startup work with lifecycle and measurement evidence.', ['AND']],
  COR: ['Explain execution context, cancellation, and structured ownership precisely.', ['KOT', 'AND']],
  FLO: ['Model streams and UI state with explicit replay and lifecycle behavior.', ['COR']],
  ARC: ['Make ownership and data flow explicit across UI, domain, and data.', ['AND', 'FLO']],
  SOL: ['Apply design principles to concrete change pressure rather than acronyms.', ['KOT', 'ARC']],
  PAT: ['Choose patterns by the problem they solve and the coupling they add.', ['SOL']],
  DI: ['Understand object graphs, bindings, scopes, and lifecycle boundaries.', ['ARC', 'SOL']],
  COM: ['Reason about composition, state, effects, and lifecycle-aware collection.', ['KOT', 'FLO']],
  DAT: ['Design durable local truth, network boundaries, and conflict handling.', ['ARC', 'COR']],
  BG: ['Match work to process, user-visible, and OS-scheduled lifetimes.', ['AND', 'COR']],
  SEC: ['Separate on-device hardening from server authority and threat models.', ['AND', 'DAT']],
  SYS: ['Turn product constraints into explicit architecture and failure decisions.', ['ARC', 'DAT', 'SEC']],
  MOD: ['Draw module boundaries around ownership and dependency direction.', ['ARC', 'DI']],
  BLD: ['Understand build, shrinking, signing, and rollout as one release chain.', ['MOD']],
  TST: ['Use tests that prove behavior at the right boundary and failure mode.', ['ARC', 'DAT']],
  CIC: ['Connect change review, automation, and release evidence.', ['TST', 'BLD']],
  DSA: ['State invariants and complexity before optimizing code.', ['KOT']],
  LEAD: ['Use evidence and clear decisions to guide teams through ambiguity.', ['SYS', 'TST']],
  PAY: ['Treat payment outcomes, retries, reversals, and sensitive data as explicit contracts.', ['SEC', 'SYS']],
};

await rm(path.join(docs, 'questions'), { recursive: true, force: true });
await rm(path.join(docs, 'topics'), { recursive: true, force: true });
await mkdir(path.join(docs, 'questions'), { recursive: true });
await mkdir(path.join(docs, 'topics'), { recursive: true });

for (const [index, q] of questions.entries()) {
  const original = await readFile(path.join(root, 'Interview-Lab/questions', `${q.id}.md`), 'utf8');
  const meta = original.match(/^---\n([\s\S]*?)\n---\n/);
  if (!meta) throw new Error(`missing frontmatter: ${q.id}`);
  const scalar = (key) => {
    const line = meta[1].split('\n').find((entry) => entry.startsWith(`${key}: `));
    if (!line) throw new Error(`missing ${key}: ${q.id}`);
    return JSON.parse(line.slice(key.length + 2));
  };
  if (scalar('id') !== q.id || scalar('question') !== q.question || scalar('code') !== q.code || scalar('group') !== q.group) {
    throw new Error(`source fidelity mismatch: ${q.id}`);
  }
  const status = scalar('editorial_status');
  if (status === 'reviewed') reviewed.push(q.id);
  else if (status === 'source-only') sourceOnly.push(q.id);
  else throw new Error(`invalid editorial status: ${q.id}`);
  const body = original.slice(meta[0].length).trimStart().replace(/^# .+\n+/, '').trim();
  const arabic = body.match(/## Explanation in Arabic\n\n([\s\S]*?)(?=\n## |$)/)?.[1] ?? '';
  searchText[q.id] = arabic.slice(0, 1200);
  const previous = questions[index - 1];
  const next = questions[index + 1];
  const route = (item) => href(`lab/questions/${item.id.toLowerCase()}/`);
  const navigation = `<nav class="lab-adjacent" aria-label="Question navigation">${previous ? `<a href="${route(previous)}">← ${previous.id}</a>` : '<span></span>'}${next ? `<a href="${route(next)}">${next.id} →</a>` : ''}</nav>`;
  const content = `---\ntitle: ${title(`${q.id} — ${q.question}`)}\ndescription: ${title(`${q.topic} · ${q.group} · original interview question`)}\nsidebar:\n  hidden: true\n---\n\n<div class="canonical-source"><bdi>${q.id}</bdi> · ${escapeHtml(q.topic)} · Group ${q.group} · Phase ${q.phase} · ${q.priority}</div>\n\n${body}\n\n${status === 'source-only' ? '> **Editorial state:** The exact source question is preserved here. A complete technical explanation and reviewed answer have not yet been published for this ID.\n\n' : ''}<lab-question question-id="${q.id}" editorial-status="${status}"></lab-question>\n\n${navigation}\n`;
  await writeFile(path.join(docs, 'questions', `${q.id.toLowerCase()}.md`), content);
}

const codes = [...new Set(questions.map((q) => q.code))];
const rows = [];
for (const code of codes) {
  const topicQuestions = questions.filter((q) => q.code === code);
  const first = topicQuestions[0];
  const [intro, prereqs] = topicGuide[code];
  const topicRoute = href(`lab/topics/${code.toLowerCase()}/`);
  rows.push(`| [${first.topic}](${topicRoute}) | ${topicQuestions.length} | ${first.phase} | ${first.priority} |`);
  const groups = ['A', 'B', 'C'].map((group) => {
    const items = topicQuestions.filter((q) => q.group === group);
    return `## ${group} — ${group === 'A' ? 'Fundamentals' : group === 'B' ? 'Practical / Implementation' : 'Senior Scenarios / Trade-offs'}\n\n${items.map((q) => `- [${q.id}](${href(`lab/questions/${q.id.toLowerCase()}/`)}) — ${q.question}`).join('\n')}`;
  }).join('\n\n');
  const prereqLine = prereqs.length ? prereqs.map((item) => `[${item}](${href(`lab/topics/${item.toLowerCase()}/`)})`).join(' · ') : 'No required earlier topic';
  await writeFile(path.join(docs, 'topics', `${code.toLowerCase()}.md`), `---\ntitle: ${title(`${code} — ${first.topic}`)}\ndescription: ${title(`${topicQuestions.length} canonical questions · Phase ${first.phase}`)}\n---\n\n<div class="lab-topic-marker"></div>\n\n${intro}\n\n**${topicQuestions.length} source questions** · Phase ${first.phase} · ${first.priority}. The A/B/C grouping follows the original bank.\n\n**Suggested prerequisites:** ${prereqLine}.\n\n<lab-topic topic-code="${code}"></lab-topic>\n\n${groups}\n`);
}
await writeFile(path.join(docs, 'index.md'), `---\ntitle: Android Interview Lab\ndescription: 485 source questions across 21 Android engineering topics\n---\n\nThe supplied bank has **485 exact source questions across 21 topics**. Each question has a stable route. Educational answer coverage is shown honestly on each page; source-only pages are available for independent practice and are not presented as reviewed lessons.\n\n<lab-dashboard></lab-dashboard>\n\n## Explore the five phases\n\n| Topic | Questions | Phase | Priority |\n|---|---:|---:|---|\n${rows.join('\n')}\n\n[Search and filter all questions](${href('lab/explore/')}) · [Flashcards and due reviews](${href('lab/review/')}) · [Mock interview](${href('lab/practice/')})\n`);
await mkdir(path.join(siteRoot, 'public/data'), { recursive: true });
await writeFile(path.join(siteRoot, 'public/data/interview-lab.json'), JSON.stringify({ generatedAt: new Date().toISOString(), questions: questions.map((q) => ({ ...q, searchText: searchText[q.id], editorialStatus: reviewed.includes(q.id) ? 'reviewed' : 'source-only' })) }));
console.log(`Interview Lab: ${questions.length} routes, ${reviewed.length} reviewed, ${sourceOnly.length} source-only`);
