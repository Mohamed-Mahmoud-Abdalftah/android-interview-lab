import { mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { href } from './site-base.mjs';

const siteRoot = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const root = path.dirname(siteRoot);
const docs = path.join(siteRoot, 'src/content/docs/lab');
const docsAr = path.join(siteRoot, 'src/content/docs/ar/lab');
const manifest = JSON.parse(await readFile(path.join(root, 'reports/source-manifest.json'), 'utf8'));
const questions = manifest.questions;

let arabicMetadata = {};
try {
  arabicMetadata = JSON.parse(await readFile(path.join(root, 'scripts/elevations/data/arabic_lab_metadata.json'), 'utf8'));
} catch {
  arabicMetadata = {};
}

const title = (value) => JSON.stringify(value);
const escapeHtml = (value) => value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const sourceOnly = [];
const reviewed = [];
const searchText = {};
const searchTextAr = {};

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

const topicGuideAr = {
  KOT: ['افهم وتتبع دلالات وقواعد Kotlin بعمق قبل الانتقال لمستوى الـ Framework.', []],
  AND: ['تتبع دورات حياة الـ Activity والعملية والـ Context قبل تحديد مالك الحالة (State Owner).', ['KOT']],
  MEM: ['شخص تسريبات الذاكرة والـ ANRs وبدء التشغيل بالأدلة القياسية وذاكرة النظام.', ['AND']],
  COR: ['اشرح سياق التنفيذ والإلغاء المنسق والملكية المهيكلة بدقة متناهية.', ['KOT', 'AND']],
  FLO: ['ابنِ تدفقات البيانات وحالة الواجهة مع نمذجة واضحة لإعادة البث ودورة الحياة.', ['COR']],
  ARC: ['اجعل ملكية البيانات واتجاه تدفقها صريحاً عبر طبقات الواجهة والنطاق والبيانات.', ['AND', 'FLO']],
  SOL: ['طبق مبادئ التصميم لمواجهة ضغوط التغيير الفعلية بدلاً من حفظ الاختصارات.', ['KOT', 'ARC']],
  PAT: ['اختر النمط بناءً على المشكلة التي يحلها ودرجة الاقتران (Coupling) التي يضيفها.', ['SOL']],
  DI: ['افهم رسوم الكائنات والـ Bindings ونطاقات الـ Scopes وحدود دورة الحياة.', ['ARC', 'SOL']],
  COM: ['حلل عمليات الـ Composition والحالة والـ Effects وجمع البيانات الآمن دورياً.', ['KOT', 'FLO']],
  DAT: ['صمم مصدر الحقيقة المحلي الدائم، وحدود الشبكة، ومعالجة التعارضات.', ['ARC', 'COR']],
  BG: ['طابق نوع العمل مع عمر العملية، وظهورها للمستخدم، والمهام المجدولة.', ['AND', 'COR']],
  SEC: ['افصل بين حماية الجهاز وسلطة السيرفر ونماذج التهديد المالي.', ['AND', 'DAT']],
  SYS: ['حول متطلبات المنتج لقرارات معمارية واضحة وحلول صريحة لحالات الفشل.', ['ARC', 'DAT', 'SEC']],
  MOD: ['ارسم حدود الموديولات حول الملكية المستقلة واتجاه التبعيات السليم.', ['ARC', 'DI']],
  BLD: ['افهم دورة البناء والتقليص والتوقيع والإطلاق كسلسلة تسليم واحدة.', ['MOD']],
  TST: ['اعتمد على اختبارات تثبت السلوك عند الحدود الصحيحة وتكشف حالات الانهيار.', ['ARC', 'DAT']],
  CIC: ['اربط بين مراجعة الكود والأتمتة وأدلة سلامة الإطلاق في الفريق.', ['TST', 'BLD']],
  DSA: ['حدد الـ Invariants والتعقيد الحسابي (Big O) قبل البدء في كتابة أو تحسين الكود.', ['KOT']],
  LEAD: ['استند للأدلة والقرارات الشفافة لقيادة الفرق الهندسية وتجاوز الغموض.', ['SYS', 'TST']],
  PAY: ['تعامل مع عمليات الدفع، والإعادات، والتسويات، والبيانات الحساسة كعقود غير قابلة للتفريط.', ['SEC', 'SYS']],
};

const topicArNames = {
  KOT: 'أساسيات لغة Kotlin ومفاهيمها المتقدمة',
  AND: 'أساسيات أندرويد ودورة الحياة والسياق (Context)',
  MEM: 'إدارة الذاكرة والـ ANR وتحسين الأداء',
  COR: 'الـ Coroutines والتزامن في Kotlin',
  FLO: 'الـ Flow و StateFlow و SharedFlow والـ Channels',
  ARC: 'العمارة النظيفة و MVVM و MVI و UDF',
  SOL: 'مبادئ SOLID والتصميم الكائني',
  PAT: 'أنماط التصميم البرمجية (Design Patterns)',
  DI: 'حقن التبعيات: Hilt و Dagger',
  COM: 'واجهات Jetpack Compose الحديثة',
  DAT: 'الشبكات وقواعد بيانات Room والـ DataStore والتخزين المحلي',
  BG: 'المهام الخلفية و WorkManager وقيود النظام',
  SEC: 'أمان أندرويد والتشفير والنمذجة الأمنية لتطبيقات التكنولوجيا المالية',
  SYS: 'تصميم أنظمة وتطبيقات الموبايل (System Design) والقرارات الهندسية',
  MOD: 'تقسيم المشروع لموديولات (Modularization) وحدود التبعيات',
  BLD: 'أنظمة البناء و Gradle و AGP و R8 والـ Signing وإصدار التطبيقات',
  TST: 'اختبار البرمجيات والجودة والموثوقية',
  CIC: 'الـ CI/CD والـ Git وتسليم المشاريع في الفرق الهندسية',
  DSA: 'هياكل البيانات والخوارزميات والـ Big O',
  LEAD: 'القيادة التقنية والتواصل وملكية المشاريع الهندسية',
  PAY: 'سيناريوهات الدفع ونقاط البيع (POS) وتأمين المعاملات المالية',
};

// Clean output directories
await rm(path.join(docs, 'questions'), { recursive: true, force: true });
await rm(path.join(docs, 'topics'), { recursive: true, force: true });
await rm(path.join(docsAr, 'questions'), { recursive: true, force: true });
await rm(path.join(docsAr, 'topics'), { recursive: true, force: true });
await mkdir(path.join(docs, 'questions'), { recursive: true });
await mkdir(path.join(docs, 'topics'), { recursive: true });
await mkdir(path.join(docsAr, 'questions'), { recursive: true });
await mkdir(path.join(docsAr, 'topics'), { recursive: true });

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
  const sections = {};
  for (const part of body.split(/(?:^|\n)## /g)) {
    if (!part.trim()) continue;
    const firstNewline = part.indexOf('\n');
    const title = firstNewline === -1 ? part.trim() : part.slice(0, firstNewline).trim();
    const secContent = firstNewline === -1 ? '' : part.slice(firstNewline + 1).trim();
    sections[title] = secContent;
  }

  const qAr = arabicMetadata[q.id] || {};
  const questionAr = qAr.questionAr || q.question;
  const topicAr = qAr.topicAr || topicArNames[q.code] || q.topic;

  // Search text indexing for both languages
  const arabicExpl = sections['Explanation in Arabic'] || '';
  searchText[q.id] = (sections['Interview answer — structured'] || sections['Why it matters and how it works'] || '').slice(0, 800);
  searchTextAr[q.id] = (questionAr + ' ' + arabicExpl.slice(0, 1000));

  const previous = questions[index - 1];
  const next = questions[index + 1];

  // 1. Generate English Question Page (100% English, NO Arabic)
  const routeEn = (item) => href(`lab/questions/${item.id.toLowerCase()}/`);
  const navEn = `<nav class="lab-adjacent" aria-label="Question navigation">${previous ? `<a href="${routeEn(previous)}">← ${previous.id}</a>` : '<span></span>'}${next ? `<a href="${routeEn(next)}">${next.id} →</a>` : ''}</nav>`;

  const enSections = [
    `## Original interview question\n\n${q.question}`,
    sections['What the interviewer evaluates'] ? `## What the interviewer evaluates\n\n${sections['What the interviewer evaluates']}` : '',
    sections['Why it matters and how it works'] ? `## Why it matters and how it works\n\n${sections['Why it matters and how it works']}` : '',
    sections['Worked example'] ? `## Worked example\n\n${sections['Worked example']}` : '',
    sections['Trade-offs and decision criteria'] ? `## Trade-offs and decision criteria\n\n${sections['Trade-offs and decision criteria']}` : '',
    sections['Failure modes'] ? `## Failure modes\n\n${sections['Failure modes']}` : '',
    sections['Production perspective'] ? `## Production perspective\n\n${sections['Production perspective']}` : '',
    sections['Interview answer — short'] ? `## Interview answer — short\n\n${sections['Interview answer — short']}` : '',
    sections['Interview answer — structured'] ? `## Interview answer — structured\n\n${sections['Interview answer — structured']}` : '',
    sections['Interview answer — deep senior'] ? `## Interview answer — deep senior\n\n${sections['Interview answer — deep senior']}` : '',
    sections['How to answer in the interview'] ? `## How to answer in the interview\n\n${sections['How to answer in the interview']}` : '',
    sections['Deep-dive talking points'] ? `## Deep-dive talking points\n\n${sections['Deep-dive talking points']}` : '',
    sections['Follow-up questions'] ? `## Follow-up questions\n\n${sections['Follow-up questions']}` : '',
    sections['Self-check rubric'] ? `## Self-check rubric\n\n${sections['Self-check rubric']}` : '',
    sections['References and reviewed-on date'] ? `## References and reviewed-on date\n\n${sections['References and reviewed-on date']}` : '',
  ].filter(Boolean).join('\n\n');

  const enContent = `---\ntitle: ${title(`${q.id} — ${q.question}`)}\ndescription: ${title(`${q.topic} · Group ${q.group} · Phase ${q.phase}`)}\nsidebar:\n  hidden: true\n---\n\n<div class="canonical-source"><bdi>${q.id}</bdi> · ${escapeHtml(q.topic)} · Group ${q.group} · Phase ${q.phase} · ${q.priority}</div>\n\n${enSections}\n\n${status === 'source-only' ? '> **Editorial state:** The exact source question is preserved here. A complete technical explanation and reviewed answer have not yet been published for this ID.\n\n' : ''}<lab-question question-id="${q.id}" editorial-status="${status}"></lab-question>\n\n${navEn}\n`;

  await writeFile(path.join(docs, 'questions', `${q.id.toLowerCase()}.md`), enContent, 'utf8');

  // 2. Generate Arabic Question Page (100% Arabic with English LTR code & terms)
  const routeAr = (item) => href(`ar/lab/questions/${item.id.toLowerCase()}/`);
  const navAr = `<nav class="lab-adjacent" aria-label="التنقل بين الأسئلة">${previous ? `<a href="${routeAr(previous)}">← ${previous.id}</a>` : '<span></span>'}${next ? `<a href="${routeAr(next)}">${next.id} →</a>` : ''}</nav>`;

  const arSections = [
    `## السؤال الأصلي في المقابلة\n\n<p dir="ltr" lang="en"><code>${q.question}</code></p>\n\n> **الترجمة والسياق العربي:** ${questionAr}`,
    sections['What the interviewer evaluates'] ? `## ما يقيّمه المحاور\n\n${sections['What the interviewer evaluates']}` : '',
    sections['Explanation in Arabic'] ? `## الشرح والمفهوم التقني\n\n${sections['Explanation in Arabic']}` : '',
    sections['Practical walkthrough'] ? `## التطبيق العملي وسيناريو الفشل\n\n${sections['Practical walkthrough']}` : '',
    sections['Why it matters and how it works'] ? `## آلية العمل والتحليل الهندسي\n\n${sections['Why it matters and how it works']}` : '',
    sections['Worked example'] ? `## مثال تطبيقي واختبار\n\n${sections['Worked example']}` : '',
    sections['Trade-offs and decision criteria'] ? `## المفاضلات الهندسية ومعايير القرار\n\n${sections['Trade-offs and decision criteria']}` : '',
    sections['Failure modes'] ? `## أنماط الفشل ومصائد الأخطاء\n\n${sections['Failure modes']}` : '',
    sections['Production perspective'] ? `## منظور بيئة العمل الفعلي (Production)\n\n${sections['Production perspective']}` : '',
    qAr.quick_answer_ar || sections['Interview answer — short'] ? `## إجابة المقابلة — ملخصة وسريعة\n\n${qAr.quick_answer_ar || sections['Interview answer — short']}` : '',
    qAr.best_answer_ar || sections['Interview answer — structured'] ? `## إجابة المقابلة — نموذجية ومهيكلة\n\n${qAr.best_answer_ar || sections['Interview answer — structured']}` : '',
    qAr.deep_answer_ar || sections['Interview answer — deep senior'] ? `## إجابة المقابلة — مناقشة Senior متعمقة\n\n${qAr.deep_answer_ar || sections['Interview answer — deep senior']}` : '',
    sections['How to answer in the interview'] ? `## طريقة تقديم الإجابة في المقابلة\n\n${sections['How to answer in the interview']}` : '',
    sections['Deep-dive talking points'] ? `## محاور النقاش المتقدم\n\n${sections['Deep-dive talking points']}` : '',
    qAr.follow_ups_ar || sections['Follow-up questions'] ? `## أسئلة المتابعة واعتراضات المحاور\n\n${qAr.follow_ups_ar || sections['Follow-up questions']}` : '',
    sections['Self-check rubric'] ? `## معايير التقييم الذاتي\n\n${sections['Self-check rubric']}` : '',
    sections['References and reviewed-on date'] ? `## المراجع وتاريخ المراجعة الفنية\n\n${sections['References and reviewed-on date']}` : '',
  ].filter(Boolean).join('\n\n');

  const arContent = `---\ntitle: ${title(`${q.id} — ${questionAr}`)}\ndescription: ${title(`${topicAr} · المجموعة ${q.group} · المرحلة ${q.phase}`)}\nsidebar:\n  hidden: true\n---\n\n<div class="canonical-source"><bdi>${q.id}</bdi> · ${escapeHtml(topicAr)} · المجموعة ${q.group} · المرحلة ${q.phase} · ${q.priority}</div>\n\n${arSections}\n\n${status === 'source-only' ? '> **حالة المحتوى:** السؤال محفوظ بالصيغة الأصلية. الشرح والإجابة المعتمدة قيد الإعداد.\n\n' : ''}<lab-question question-id="${q.id}" editorial-status="${status}"></lab-question>\n\n${navAr}\n`;

  await writeFile(path.join(docsAr, 'questions', `${q.id.toLowerCase()}.md`), arContent, 'utf8');
}

// Generate Topic Guides in English and Arabic
const codes = [...new Set(questions.map((q) => q.code))];
const rowsEn = [];
const rowsAr = [];

for (const code of codes) {
  const topicQuestions = questions.filter((q) => q.code === code);
  const first = topicQuestions[0];
  const topicArName = topicArNames[code] || first.topic;
  const [introEn, prereqsEn] = topicGuide[code] || [first.topic, []];
  const [introAr, prereqsAr] = topicGuideAr[code] || [topicArName, []];

  const topicRouteEn = href(`lab/topics/${code.toLowerCase()}/`);
  const topicRouteAr = href(`ar/lab/topics/${code.toLowerCase()}/`);

  rowsEn.push(`| [${first.topic}](${topicRouteEn}) | ${topicQuestions.length} | ${first.phase} | ${first.priority} |`);
  rowsAr.push(`| [${topicArName}](${topicRouteAr}) | ${topicQuestions.length} | ${first.phase} | ${first.priority} |`);

  // English topic groups
  const groupsEn = ['A', 'B', 'C'].map((group) => {
    const items = topicQuestions.filter((q) => q.group === group);
    return `## ${group} — ${group === 'A' ? 'Fundamentals' : group === 'B' ? 'Practical / Implementation' : 'Senior Scenarios / Trade-offs'}\n\n${items.map((q) => `- [${q.id}](${href(`lab/questions/${q.id.toLowerCase()}/`)}) — ${q.question}`).join('\n')}`;
  }).join('\n\n');

  const prereqLineEn = prereqsEn.length ? prereqsEn.map((item) => `[${item}](${href(`lab/topics/${item.toLowerCase()}/`)})`).join(' · ') : 'No required earlier topic';

  await writeFile(path.join(docs, 'topics', `${code.toLowerCase()}.md`), `---\ntitle: ${title(`${code} — ${first.topic}`)}\ndescription: ${title(`${topicQuestions.length} canonical questions · Phase ${first.phase}`)}\n---\n\n<div class="lab-topic-marker"></div>\n\n${introEn}\n\n**${topicQuestions.length} source questions** · Phase ${first.phase} · ${first.priority}. The A/B/C grouping follows the original bank.\n\n**Suggested prerequisites:** ${prereqLineEn}.\n\n<lab-topic topic-code="${code}"></lab-topic>\n\n${groupsEn}\n`, 'utf8');

  // Arabic topic groups
  const groupsAr = ['A', 'B', 'C'].map((group) => {
    const items = topicQuestions.filter((q) => q.group === group);
    const grpName = group === 'A' ? 'الأساسيات والمفاهيم الجوهرية' : group === 'B' ? 'التطبيق العملي وبناء الميزات' : 'سيناريوهات الـ Senior والمفاضلات الهندسية';
    return `## ${group} — ${grpName}\n\n${items.map((q) => {
      const qAr = arabicMetadata[q.id] || {};
      return `- [${q.id}](${href(`ar/lab/questions/${q.id.toLowerCase()}/`)}) — ${qAr.questionAr || q.question}`;
    }).join('\n')}`;
  }).join('\n\n');

  const prereqLineAr = prereqsAr.length ? prereqsAr.map((item) => `[${item}](${href(`ar/lab/topics/${item.toLowerCase()}/`)})`).join(' · ') : 'لا يوجد موضوع سابق إلزامي';

  await writeFile(path.join(docsAr, 'topics', `${code.toLowerCase()}.md`), `---\ntitle: ${title(`${code} — ${topicArName}`)}\ndescription: ${title(`${topicQuestions.length} أسئلة معتمدة · المرحلة ${first.phase}`)}\n---\n\n<div class="lab-topic-marker"></div>\n\n${introAr}\n\n**${topicQuestions.length} سؤال معتمد** · المرحلة ${first.phase} · ${first.priority}.\n\n**المتطلبات السابقة المقترحة:** ${prereqLineAr}.\n\n<lab-topic topic-code="${code}"></lab-topic>\n\n${groupsAr}\n`, 'utf8');
}

// Generate Core Lab Pages (English)
await writeFile(path.join(docs, 'index.md'), `---\ntitle: Android Interview Lab\ndescription: 485 source questions across 21 Android engineering topics\n---\n\nThe supplied bank has **485 exact source questions across 21 topics**. Each question has a stable route. Educational answer coverage is shown honestly on each page; source-only pages are available for independent practice and are not presented as reviewed lessons.\n\n<lab-dashboard></lab-dashboard>\n\n## Explore the five phases\n\n| Topic | Questions | Phase | Priority |\n|---|---:|---:|---|\n${rowsEn.join('\n')}\n\n[Search and filter all questions](${href('lab/explore/')}) · [Flashcards and due reviews](${href('lab/review/')}) · [Mock interview](${href('lab/practice/')})\n`, 'utf8');

await writeFile(path.join(docs, 'explore.md'), `---\ntitle: Explore all canonical questions\ndescription: Search and filter the supplied 485-question Android interview bank\n---\n\nSearch by ID, technical term, or question wording. Filter by original topic, phase, A/B/C group, and your local progress. Each result shows its editorial status.\n\n<lab-explorer></lab-explorer>\n\nStarlight site search also indexes the earlier academy lessons and model answers.\n`, 'utf8');

await writeFile(path.join(docs, 'review.md'), `---\ntitle: Flashcards and due reviews\ndescription: Browser-local spaced repetition for Android interview questions\n---\n\nAnswer from memory, then grade your recall. **Again** returns the card today; **Hard**, **Good**, and **Easy** set growing local-day intervals. The schedule is a practice aid, not proof of mastery.\n\n<lab-review></lab-review>\n`, 'utf8');

await writeFile(path.join(docs, 'practice.md'), `---\ntitle: Mock interview\ndescription: Timed, self-rated Android interview practice\n---\n\nChoose 10, 20, 30, or 45 minutes and a topic or mixed session. Write your answer before revealing the question page. Every canonical ID now has an authored answer. Ratings are self-assessed and local.\n\n<lab-practice></lab-practice>\n\n## Self-check rubric\n\nCheck your definition, mechanism, Android/Kotlin example, failure or edge case, and justified production decision. For design or leadership questions, use a concrete decision and evidence in place of code. No automatic technical score is calculated.\n`, 'utf8');

await writeFile(path.join(docs, 'plans.md'), `---\ntitle: Study plans\ndescription: Seven, fourteen, and thirty day Android interview study schedules\n---\n\nUse the topic pages and set your daily question goal on the [Lab dashboard](../). Spend part of each session on first attempts and part on due reviews. These schedules do not imply source-only answers have been reviewed.\n\n## 7 days · focused refresh\n\n| Day | Focus |\n|---|---|\n| 1 | Kotlin, Android fundamentals, memory |\n| 2 | Coroutines and Flow |\n| 3 | Architecture, SOLID, patterns, DI |\n| 4 | Compose, data, background work |\n| 5 | Security, payments, system design |\n| 6 | Modularization, build/release, testing, CI/CD |\n| 7 | Algorithms, leadership, timed mock and weak areas |\n\n## 14 days · balanced practice\n\nSpend days 1–5 on Phase 1, days 6–8 on Phase 2, days 9–11 on Phase 3, days 12–13 on Phase 4, and day 14 on Phase 5 plus a mock interview. Review due cards every day.\n\n## 30 days · deeper pass\n\nAllocate one day to each of the 21 topics in original phase order. Use days 22–26 for cross-topic paths (Coroutines → Flow → Compose; Lifecycle → Memory → Background Work; Architecture → SOLID → DI → Modules; Security → Payments → System Design; Testing → CI/CD → Release). Use days 27–30 for due reviews, two timed mocks, and weak areas.\n`, 'utf8');

// Generate Core Lab Pages (Arabic)
await writeFile(path.join(docsAr, 'index.md'), `---\ntitle: مختبر أسئلة أندرويد\ndescription: 485 سؤالاً معتمداً من مقابلات كبرى الشركات التقنية عبر 21 موضوعاً في هندسة أندرويد\n---\n\nيحتوي بنك الأسئلة المعتمد على **485 سؤالاً تقنياً موزعة على 21 موضوعاً**. لكل سؤال مسار ثابت وتغطية تعليمية دقيقة ومراجعة برمجية كاملة.\n\n<lab-dashboard></lab-dashboard>\n\n## استكشف المراحل الخمس\n\n| الموضوع | عدد الأسئلة | المرحلة | الأولوية |\n|---|---:|---:|---|\n${rowsAr.join('\n')}\n\n[البحث والفلترة في كل الأسئلة](${href('ar/lab/explore/')}) · [البطاقات التعليمية والمراجعة](${href('ar/lab/review/')}) · [المقابلة التجريبية](${href('ar/lab/practice/')})\n`, 'utf8');

await writeFile(path.join(docsAr, 'explore.md'), `---\ntitle: استكشف جميع الأسئلة المعتمدة\ndescription: ابحث وفلتر في بنك أسئلة أندرويد الكامل المكون من 485 سؤالاً\n---\n\nابحث برمز السؤال، المصطلح التقني، أو نص السؤال. يمكنك الفلترة حسب الموضوع، المرحلة، مجموعة الصعوبة، وحالة تقدمك المحفوظة محلياً.\n\n<lab-explorer></lab-explorer>\n\nبحث الموقع في الشريط العلوي يبحث أيضاً في كافة الدروس والإجابات النموذجية.\n`, 'utf8');

await writeFile(path.join(docsAr, 'review.md'), `---\ntitle: البطاقات التعليمية والمراجعة المتباعدة\ndescription: نظام تكرار متباعد محلي في المتصفح لأسئلة مقابلات أندرويد\n---\n\nأجب من ذاكرتك أولاً، ثم قيّم استرجاعك. زر **إعادة** يعيد البطاقة اليوم؛ وأزرار **صعب** و**جيد** و**سهل** تزيد الفترات الزمنية للمراجعة.\n\n<lab-review></lab-review>\n`, 'utf8');

await writeFile(path.join(docsAr, 'practice.md'), `---\ntitle: محاكاة المقابلات التجريبية\ndescription: جلسات تدريب مؤقتة وتقييم ذاتي لمقابلات أندرويد الحقيقية\n---\n\nاختر مدة الجلسة (10، 20، 30، أو 45 دقيقة) وحدد موضوعاً معيناً أو جلسة شاملة. اكتب إجابتك الخاصة قبل الكشف عن نموذج الإجابة. جميع التقييمات ذاتية ومحفوظة في متصفحك.\n\n<lab-practice></lab-practice>\n\n## معايير التقييم الذاتي\n\nتأكد من شمول إجابتك للتعريف الدقيق، الآلية الداخلية للنظام، الكود، حالات الفشل أو الحالات الحدية، والمبررات الهندسية في الـ Production.\n`, 'utf8');

await writeFile(path.join(docsAr, 'plans.md'), `---\ntitle: خطط المذاكرة المنظمة\ndescription: جداول مذاكرة مركزة لمقابلات أندرويد لـ 7 أيام و 14 يوماً و 30 يوماً\n---\n\nاستخدم صفحات المواضيع وحدد هدفك اليومي من الأسئلة في [لوحة التحكم](../). قسّم وقتك بين الأسئلة الجديدة ومراجعة البطاقات المستحقة.\n\n## 7 أيام · مراجعة سريعة ومركزة\n\n| اليوم | التركيز |\n|---|---|\n| 1 | كوتلن، أساسيات أندرويد، إدارة الذاكرة |\n| 2 | الـ Coroutines والـ Flow |\n| 3 | المعمارية، مبادئ SOLID، أنماط التصميم، حقن التبعيات |\n| 4 | واجهات Compose، قواعد البيانات، العمليات الخلفية |\n| 5 | الأمان، سيناريوهات الدفع، تصميم الأنظمة (System Design) |\n| 6 | تقسيم الموديولات، البناء والإطلاق، الاختبارات، الـ CI/CD |\n| 7 | الخوارزميات، القيادة التقنية، جلسات محاكاة ونقاط الضعف |\n\n## 14 يوماً · تدريب متوازن\n\nخصص الأيام 1–5 للمرحلة الأولى، والأيام 6–8 للمرحلة الثانية، والأيام 9–11 للمرحلة الثالثة، والأيام 12–13 للمرحلة الرابعة، واليوم 14 للمرحلة الخامسة مع جلسة محاكاة كاملة.\n\n## 30 يوماً · تعمق شامل\n\nخصص يوماً كاملاً لكل موضوع من الـ 21 موضوعاً. استخدم الأيام 22–26 للمسارات المترابطة (Coroutines → Flow → Compose; Lifecycle → Memory → Background Work; Architecture → SOLID → DI → Modules; Security → Payments → System Design; Testing → CI/CD → Release). وخصص الأيام 27–30 للمراجعة المتباعدة ومقابلتين تجريبيتين.\n`, 'utf8');

// Write public data interview-lab.json with full bilingual search index
await mkdir(path.join(siteRoot, 'public/data'), { recursive: true });
const labData = {
  generatedAt: new Date().toISOString(),
  questions: questions.map((q) => {
    const qAr = arabicMetadata[q.id] || {};
    return {
      ...q,
      questionAr: qAr.questionAr || q.question,
      topicAr: qAr.topicAr || topicArNames[q.code] || q.topic,
      route: href(`lab/questions/${q.id.toLowerCase()}/`),
      routeAr: href(`ar/lab/questions/${q.id.toLowerCase()}/`),
      searchText: searchText[q.id] || '',
      searchTextAr: searchTextAr[q.id] || '',
      editorialStatus: reviewed.includes(q.id) ? 'reviewed' : 'source-only',
    };
  }),
};
await writeFile(path.join(siteRoot, 'public/data/interview-lab.json'), JSON.stringify(labData), 'utf8');

console.log(`Interview Lab Bilingual: ${questions.length} routes generated in both EN and AR (Total ${questions.length * 2} question pages).`);

