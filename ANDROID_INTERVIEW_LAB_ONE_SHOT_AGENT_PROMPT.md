# ANDROID INTERVIEW LAB — ONE-SHOT, PRODUCTION-READY MASTER IMPLEMENTATION PROMPT

> **Give this entire prompt and the attached `Senior_Android_Interview_Master_Bank.md` to the coding agent in the root of the target repository.** If you also have an existing Android Academy repository, open that repository as the working directory before starting. Your assignment is to implement, populate, verify, and deploy the actual product — not to propose a plan or create a proof of concept.

## 0. Your mission and non-negotiable operating mode

You are acting as the **Principal Android Engineer, Staff-level Technical Interviewer, Learning Experience Designer, Content Editor, Frontend Architect, QA Engineer, and Release Engineer** for a single finished product:

**ANDROID INTERVIEW LAB — Learn deeply. Explain clearly. Answer like a Senior Android Engineer.**

This is an end-to-end implementation request. **Do the work, don't merely describe the work.** You own discovery, architecture, design, content, data migration, code, tests, documentation, CI, GitHub Pages deployment readiness, and final verification. Work autonomously from this prompt and the supplied question bank. Do not repeatedly ask for UI approval, tool choices, or whether to continue from one topic to the next. Make sensible engineering decisions, execute them, and document them. Do not stop at a UI mockup, a sample chapter, an outline, an empty CMS, a few examples, or a partly populated site. Do not replace real content with boilerplate just to pass counters.

**Important realism rule:** You may take as many internal iterations, batch runs, reviews, commits, and automated checks as your available execution environment permits. However, do not lie about completion. If an external permission (GitHub write access, Pages settings, or deployment credentials) or an actual platform/runtime limit blocks you, finish everything technically possible, save a reproducible checkpoint, explicitly list the remaining blocker, and never claim the site is live or that 485 answers are complete unless independently verified. One user instruction should suffice; do not turn routine implementation choices into a series of user questions.

### Immutable source contract

The canonical attached input is `Senior_Android_Interview_Master_Bank.md`. It contains **485 distinct questions across 21 topics**. Every question already has an immutable ID such as `KOT-01`, `COR-11`, `FLO-01`, `SEC-01` and `PAY-15`.

The expected source topic/count inventory is:

| Code | Topic | Count |
|---|---|---:|
| KOT | Kotlin Core & Advanced | 30 |
| AND | Android Fundamentals, Lifecycle & Context | 25 |
| MEM | Memory Management, ANR & Performance | 26 |
| COR | Kotlin Coroutines & Concurrency | 32 |
| FLO | Flow, StateFlow, SharedFlow & Channels | 32 |
| ARC | Clean Architecture, MVVM, MVI & UDF | 26 |
| SOL | SOLID & Object-Oriented Design | 20 |
| PAT | Design Patterns | 18 |
| DI | Dependency Injection: Hilt & Dagger | 20 |
| COM | Jetpack Compose | 28 |
| DAT | Networking, Room, DataStore & Offline-First | 22 |
| BG | Background Work, WorkManager & OS Constraints | 18 |
| SEC | Android Security, Crypto & Fintech Threat Modeling | 32 |
| SYS | Android System Design & Architecture Decisions | 24 |
| MOD | Gradle Modularization & Dependency Boundaries | 21 |
| BLD | Gradle, AGP, R8, Signing & Release Engineering | 21 |
| TST | Testing, Quality & Reliability | 24 |
| CIC | CI/CD, Git & Team Delivery | 20 |
| DSA | Data Structures, Algorithms & Big O | 16 |
| LEAD | Senior Ownership, Communication & Technical Leadership | 15 |
| PAY | Payment/POS & Security Scenarios | 15 |
| **TOTAL** | **21 topics** | **485** |

**Do not silently remove, rename, merge, replace or drop any original question.** Preserve the exact ID, original English question, original topic, and original ordering/group A/B/C. You may add editorial headings, tags, prerequisites and improved supplementary questions, but any extra question gets its own separate ID namespace and must not be included in the 485 source-preservation count. If the uploaded source differs from the above manifest, parse the actual source, produce a discrepancy report, and preserve its actual distinct questions rather than fabricating missing entries.

## 1. Inspect the existing repository FIRST: no destructive rewrite

1. Identify repository root, current branch, git status, existing `site/`, `src/`, tests, workflows, package manager, toolchains, docs, and any prior Android Academy work.
2. Read `README`, any agent instructions, existing curricula, MD/MDX, tests and deployed-site configuration before choosing an implementation path.
3. If the repository already contains Astro/Starlight, preserve and improve it. **Do not scaffold a second competing site or delete old lessons.** Integrate this Interview Lab as its own cohesive area or upgrade the existing academy as appropriate. Preserve all valuable pre-existing materials, routes, and functionality. Where IDs or navigation conflict, introduce migrations/redirects.
4. If no suitable site exists, create the site in `site/` using modern Astro + Starlight, Astro content collections, TypeScript and small client-side interactive islands.
5. Record an initial audit in `docs/IMPLEMENTATION_AUDIT.md`: files found, retained modules, source counts, relevant risks and implementation decisions. Create a tracked checklist and execution checkpoints (`docs/EXECUTION_PROGRESS.md`); update them as you work.
6. Avoid unrelated code churn. Never delete user work or rewrite git history. Do not expose any secrets. Respect the repository's chosen package manager if sound; otherwise justify a single well-supported package manager and commit its lockfile.

## 2. Deliverable and product positioning

Deliver a polished, content-rich, **free, static-first, GitHub Pages-compatible Interview Preparation Platform**. Audience: mid-level → senior Android engineers who understand technical English but want a genuinely deep Arabic explanation and practice producing strong English interview answers.

The product must work as a **real self-study and interview practice experience**, not only a list of questions. The three primary user journeys are:

- **Study:** choose topic → open question → first try answering → understand the concept in Arabic → study Why/How, Android code, trade-offs/failures and production design → rehearse concise English answer.
- **Practice:** select question or timed mock interview → hide solution → type or optionally record personal answer → compare against a transparent evidence-based rubric → self-rate and schedule review.
- **Revise:** dashboard identifies weak topics and due flashcards → spaced repetition → bookmarks, search, study plans and visible progress.

Everything required for these journeys must function on desktop and mobile without login and without a paid backend. Optimize for clarity and genuinely useful learning, not animations for their own sake.

## 3. Information architecture and curriculum

Preserve the supplied **21 topics** and group every topic into the existing source levels:

- **A — Fundamentals:** precise definitions, mental models, essential vocabulary.
- **B — Practical / Implementation:** how the API/pattern is actually used in Kotlin or Android.
- **C — Senior Scenarios / Trade-offs:** production constraints, failure handling, alternative approaches, design reviews.

Allow filtering by phase (the five phases from the source file), topic, A/B/C, P1/P2, difficulty, estimated study time, tags, bookmarked, unseen, mastered, and due review. Design optional cross-topic learning paths such as: Coroutines → Flow → Compose; Android Lifecycle → Memory → Background Work; Clean Architecture → SOLID → DI → Modularization; Security → Payments/System Design; Testing → CI/CD → Release Engineering. Do not distort the original question categorization.

### Required sitemap/navigation

- Home/dashboard: curated start point, realistic progress, due questions and resume.
- All Topics: 21 cards, accurate source question counts, ordered learning phases.
- Topic detail: introduction, prerequisites, A/B/C, questions, progress and next recommendation.
- Question detail: one canonical stable route per original ID, deep-learning sections, answer training, review actions and related questions.
- Search: full-text search across ID, English question, Arabic explanation, tags and relevant code language/keywords where possible; fast and keyboard accessible.
- Study Plans: curated 7-day, 14-day, and 30-day schedules, plus custom daily goal, no backend.
- Practice / Mock Interview: timed sessions, multi-topic or topic-specific, hide/reveal answer, scoring rubrics and session recap.
- Review / Flashcards: active recall and review scheduling.
- Bookmarks and Notes: persist locally; support simple export/import.
- About/Methodology/References/Privacy: explain authorship, source fidelity, content review approach, limitations and local data handling.
- User-friendly 404, empty states, error handling and offline states.

## 4. EXACT content standard for ALL 485 questions

Build a reusable structured content model. Every original question must get its **own substantive, accurate page**; no 485 identical template paragraphs. Avoid artificial word counts that encourage filler. Write at a depth proportional to the question: short factual questions remain efficient, while architecture, concurrency, security and system design questions receive substantially more reasoning and worked examples.

### Required content sections for each question

1. **Original Interview Question:** verbatim English source question, immutable ID, topic and original A/B/C category.
2. **What the interviewer evaluates:** 2–5 specific knowledge signals or evaluation criteria; never invent company-specific interviewer behavior.
3. **Explanation in Egyptian-friendly technical Arabic:** clear, teaching-oriented, correct English technical terms preserved; explain the underlying idea, not only translation.
4. **Why it matters and how it works:** runtime mechanics or conceptual model; distinguish framework guarantees from assumptions.
5. **Android/Kotlin worked example:** when applicable, meaningful **compilable or realistically integrated** Kotlin/Android code, with imports/context/dependency assumptions and explanatory comments. For conceptual/leadership questions, use a concrete technical decision example rather than inventing irrelevant code.
6. **Trade-offs and decision criteria:** when to use it, when not to, alternatives, cost/benefit, lifecycle/thread-safety/performance implications where appropriate.
7. **Failure modes / common mistakes:** concrete pitfalls, diagnosis and fix, ideally with a wrong-versus-right explanation for challenging questions.
8. **Production perspective:** a real-world Android app example such as payments, offline-first sync, state management, process recreation, security hardening or large-team modularization. Match the topic; do not force all topics into payment examples.
9. **Interview answer — short (30–45 seconds):** clear, professional, natural English response, easily speakable.
10. **Interview answer — structured (~90 seconds):** a stronger English response using `Definition → How/Why → Example → Trade-off/Failure → Production decision`; do not pad simpler questions to hit a duration.
11. **Deep-dive talking points:** optional extension for 3-minute follow-ups, including nuance and appropriate technical vocabulary.
12. **Follow-up questions:** ideally 2–4 plausible harder questions, connected to actual IDs whenever possible; provide answer hints, not only questions.
13. **Self-check / answer rubric:** concrete assessment points (definition, mechanism, example, edge case, judgment), with an understandable score and visible missing elements.
14. **References and reviewed-on date:** authoritative documentation links for externally verifiable Android/Kotlin behavior. Links must actually support claims; mark uncertainties and version sensitivity. Include a verified review timestamp only after actual review.

Each question's content should be **distinct and tailored**, accurately address the question, and avoid incorrect blanket generalizations. No `TODO`, `TBD`, lorem ipsum, filler, repeated generic senior answers, dead references or fabricated source links on any page claimed complete. If a field is not applicable, explicitly justify its omission in the schema instead of pretending there is code or an artificial failure case.

### Correctness requirements: non-negotiable technical examples

- A Kotlin `suspend` function does not necessarily run on a background thread; `withContext` moves work only when used appropriately. A coroutine is not itself a thread. Coroutines do not automatically make blocking code non-blocking or shared mutation safe.
- Carefully distinguish failure propagation in `coroutineScope`, `supervisorScope`, `launch` and `async`; include what happens when `await()` observes an error. Do not silently swallow `CancellationException`; explain how `runCatching` can accidentally do so and use safe alternatives.
- `StateFlow` is hot, holds a current value and conflates by equality. Distinguish it from `SharedFlow`, `Channel`, lifecycle-aware collection and semantics of replay/events. Avoid falsely promising reliable one-time delivery for every event mechanism.
- `remember`, `rememberSaveable`, `ViewModel`, `SavedStateHandle` and persistence solve different scopes of state survival; do not present process death as configuration change.
- `EncryptedSharedPreferences` must **not** be presented as universally current recommended storage without checking its present deprecation status. Explain Android Keystore key management, encryption design and storage limits accurately. `local.properties` and APK obfuscation are not secret storage protections against reverse engineering.
- `Activity` context vs `Application` context requires lifecycle-appropriate use; not all activity-context use is a leak.
- Security content must distinguish client-side hardening from server-side trust. Handle Play Integrity server verification, token lifecycle, threat modeling, PIN/card-data protection, attestation limits and operational caveats accurately, without overclaiming root detection, certificate pinning, code obfuscation or native libraries.
- Financial/payment examples must distinguish **at-least-once delivery plus server idempotency** from casually promising exactly-once network execution. Address crash recovery, timeouts, reversal queues and consistency correctly. Never recommend unsafe storage of raw card or PIN data.
- Avoid blanket `@Singleton` for every Hilt dependency; distinguish DI bindings, scopes and lifecycle.
- Do not invent API methods, Kotlin syntax, gradle configuration or imports. Prefer executable unit-testable snippets and explicit version constraints.
- Avoid overpromising 100% security, 100% performance gains, 100% consistency, or device-independent behavior. Call out genuine trade-offs and assumptions.

## 5. Content ingestion, ID preservation and quality pipeline

Implement deterministic and tested scripts (`scripts/` or `site/scripts/`, whichever matches repo conventions) that:

1. Parse the attached source Markdown and extract canonical ID, exact original question text, topic, group, priority and original order.
2. Assert **485 unique IDs**, **21 topics**, each per-topic expected count, and no missing/duplicate IDs. Generate `reports/source-manifest.json` and a readable content inventory.
3. Materialize one content record/file per original ID. Use human-editable MDX/Markdown or validated typed structured data with rich MDX body. Do not leave substantive user-facing content in a giant hardcoded component or runtime LLM request.
4. Define a strict schema (Zod or equivalent) for question fields and validate all content; track authorship/references/review status accurately.
5. Detect near-duplicate explanations and generic boilerplate, broken related-question IDs, repeated sample code, blank sections, missing original question and invalid source links.
6. Keep an immutable mapping between source question and generated route; provide a generated JSON crosswalk to prove all questions are represented.
7. Make all content static/build-time and searchable, with no database or paid API dependency required to read questions.
8. Preserve existing learning content by integrating/attaching cross-references rather than silently replacing it.

**Generation is not validation.** After producing content, review it for actual correctness topic by topic, check subtle nuances against reputable up-to-date references, and fix any contradictions. Use trusted sources such as Android Developers, Kotlin/kotlinx.coroutines official docs, Gradle, OWASP MASVS and relevant official project docs. For topics not documented by one definitive official source, cite reputable primary sources and distinguish reasoned engineering recommendations from guaranteed API contracts.

### Autonomous batch execution

You may build the content through internally managed batches to protect quality and context limits, **but the requested deliverable is the completed library, not only the first batch.** Save generated files immediately, update a machine-checkable coverage manifest, perform audits after each batch, automatically continue into the next batch, and perform a final global pass. Do not stop and ask the user to prompt “continue” between normal batches. If execution limits truly interrupt the work, leave a robust idempotent resume command and accurate `completed/remaining` statistics — never mark missing content complete.

## 6. Learning and interview practice functionality

### Question page interactions

- Clear independent tabs or accordions: **Question / Understand / Why & How / Code / Trade-offs & Failures / Production / Interview Answer / Follow-ups / Practice**. Avoid burying critical details under excessive tabs on mobile; sticky navigation or reading mode is fine.
- Start with question hidden-answer mode; student can reveal parts deliberately. Provide **Copy English Answer** and **Copy Code** actions that actually work.
- Allow a user to mark **Unseen → Learning → Practicing → Confident/Mastered**, plus bookmark, personal notes and “review again.” Do not confuse viewing with mastery.
- One question can be navigated from any of its related topics and cross-reference IDs; “Previous/Next” preserves source ordering.
- Highlight code accurately, wrap long code with horizontal scroll, support LTR code blocks inside Arabic RTL, and include meaningful accessible captions.

### Flashcards and spaced repetition

- Implement an understandable and testable scheduling algorithm (SM-2-inspired or another documented deterministic approach). User choices: **Again / Hard / Good / Easy** with meaningful review intervals. Persist state locally; handle due dates robustly and respect timezone/local-day boundaries.
- Display due, overdue, new, weak, reviewed and mastered counts honestly. Never invent user progress.
- Add daily goals, streaks only when earned, resume last position, and topic-level weak-area analysis. Avoid gamification that obscures learning.

### Mock interview

- Topic-specific or mixed topic sessions; interview length options **10 / 20 / 30 / 45 minutes** or question-count mode. Include an appropriate mix of fundamentals, senior scenarios and follow-ups.
- Timer, next/previous, answer visibility toggle, optional typed personal answer, self-rating rubric, and end-of-session honest recap.
- Provide 30-second, 90-second and deep-answer practice. Never report an automatically assessed technical score if the product only collects a self-rating.
- Add selected realistic scenario prompts and “spot the bug” exercises when technically suitable, especially for coroutine cancellation, memory leak, Compose state, R8 reflection and network retry/idempotency.
- If feasible on a static site, add **local audio recording + playback** using supported browser media APIs only with user consent; explicitly handle permission denial, unsupported browsers and microphone/HTTPS requirements. Recording should remain on-device by default. Do not pretend local recording includes trustworthy AI evaluation or speech recognition. Any transcription feature must be honestly capability-detected and optional, with a typed-answer fallback. No user audio upload without explicit opt-in.
- There is no need for a deceptive “Run Kotlin” button. If no real Kotlin execution sandbox is provided, label examples as code walkthrough/solution reveal and test code offline in the repo instead.

### Progress portability

- Store bookmarks, notes, review history, interview sessions and preferences locally (IndexedDB preferred for larger content; localStorage acceptable for compact metadata with careful storage handling).
- Export/import a versioned JSON file with schema validation, helpful errors, stable question IDs, and deterministic merge/replace semantics. User must be able to back up or move progress between browsers without an account.
- Provide clear **Reset progress** with confirmation and sane schema migration/fallback on app updates. Do not let a corrupted storage entry break the site.

## 7. Product UI/UX and visual quality

The website should feel like a **premium, restrained engineering learning product** rather than a generic Starlight starter, fake SaaS landing page, or noisy dashboard.

- Distinct visual identity: “Android Interview Lab”, polished wordmark/typography, excellent spacing, consistent iconography, subtle Android/developer flavor, compact question cards, professionally styled code blocks.
- Default comfortable dark theme plus high-quality light theme; persist choice, support system theme, respect `prefers-reduced-motion`.
- Dashboard with 21-topic explorer, phase roadmap, real progress indicators, due reviews and a prominent **Continue Studying** action.
- Desktop: useful left topic navigation + center reading area + optional right on-this-page/quick navigation. Mobile: elegant navigation, usable action controls and readable Arabic paragraphs/code without horizontal page overflow.
- Interface supports **Arabic RTL and English LTR** labels/layout (Starlight i18n or a carefully justified equivalent). **Canonical questions and spoken answers remain English; explanation is idiomatic Arabic**. No need to duplicate each question’s technical content just to offer an English UI. Mixed-direction punctuation/code must render correctly.
- Accessible semantic markup, labelled controls, focus indicators, logical tab order, usable touch targets, AA-oriented contrast, keyboard shortcuts only where not disruptive, proper `aria-live` for status updates, no color-only meaning.
- Use minimal purposeful microinteractions and skeleton/empty feedback. Do not inject heavy animation libraries or oversized images that slow down study.
- Search, filtering, theme switch, review controls, and mock interview buttons must do real work, not just look functional.
- Shareable canonical question URLs, SEO title/description, favicon, robots/sitemap, reasonable Open Graph metadata, descriptive page titles and no duplicate pages.
- Responsive at ~320px phone width, common 375/390px phones, tablet, laptop and large desktop.

## 8. Architecture and technology decisions

### Preferred default stack

- **Astro + Starlight** for docs, routing and content; **TypeScript** throughout.
- **MD/MDX + content collections + Zod** for validated question content and maintainable authoring.
- **Starlight/Pagefind search** (or equivalent build-time index) with an honest and tested experience for Arabic + English terms; consider normalization/search aliases for technical synonyms.
- **Small hydrated interactive islands** using the existing repo's framework if present; otherwise use a lightweight approach. No unnecessary full SPA rewrite.
- **Vanilla CSS/CSS variables** or existing design tokens; consistent system, theme tokens and typography. Avoid adding a massive UI dependency just to make a few controls.
- **Vitest** for domain/state/content validation; **Playwright** for user journey E2E and responsive/interaction checks.
- **GitHub Actions** for checks, production build and Pages deploy. A static-first site must not require an API server to render or practice.
- Installable **PWA/offline study** if it can be made reliable with a well-maintained service worker integration, correct offline fallback and verified cache invalidation. Do not let an immature PWA break deployment or fresh content updates. At minimum, support reading cached visited pages where supported and explain offline limitations.

Versions/APIs change: **look up actual current official documentation before installing/configuring dependencies; do not copy obsolete setup snippets**. Respect lockfile and Node engine compatibility. The implementation must build reproducibly locally and on CI.

### Maintainable boundaries

Separate `content/`, `content validation`, `navigation/index/search`, `learning state`, `review scheduling`, `practice sessions`, and `UI`. No duplicate copy of the 485 questions in several components. Define stable interfaces and tests around persistent state. Use client-side hydration only for things actually interactive.

### Suggested shape (adapt to the repo; not a reason to discard existing structure)

```text
repo/
├── Senior_Android_Interview_Master_Bank.md
├── site/
│   ├── astro.config.mjs
│   ├── package.json
│   ├── src/
│   │   ├── content/                  # canonical question records / MDX
│   │   ├── components/               # reusable lesson/practice UI
│   │   ├── layouts/                  # reading and dashboard layouts
│   │   ├── pages/                    # topics, questions, practice, review...
│   │   ├── lib/                      # schemas, progress, SRS, questions
│   │   ├── styles/                   # design tokens
│   │   └── assets/
│   ├── public/
│   ├── scripts/                     # import/validate/report/check-links
│   ├── tests/
│   └── playwright.config.ts
├── .github/workflows/
│   ├── ci.yml
│   └── deploy-pages.yml
├── docs/
│   ├── IMPLEMENTATION_AUDIT.md
│   ├── EXECUTION_PROGRESS.md
│   ├── CONTENT_GUIDELINES.md
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   └── VERIFICATION_REPORT.md
└── README.md
```

## 9. GitHub Pages deployment — make it actually usable

1. Implement static prerenderable output compatible with **GitHub Pages** and GitHub Actions.
2. Detect project site versus user/organization site: correctly calculate Astro `site` and `base` (`/<repository>/` vs `/`) and avoid hardcoded absolute-root URLs. Test every internal link, asset, search worker/index and client navigation under the repository's actual subpath.
3. Use an officially supported current Pages workflow (`withastro/action` if applicable, or build/upload/deploy Pages actions), a pinned/compatible Node version and permissions no broader than required. Respect existing deployment workflow to avoid duplicate deployments.
4. Use GitHub Actions to check content manifest, lint/typecheck, unit tests, build, and ideally targeted E2E smoke tests on PRs; on default branch, deploy only after critical checks pass.
5. If an authorized GitHub account and repository are available, push the finished branch through allowed actions and verify Pages deployment and actual published URL. If repository write access or repository Pages settings are unavailable, generate complete deployment files and exact final activation instructions. **Do not report a live URL you did not verify.**
6. Make public source hosting safe: no tokens, keystores, credentials, private applicant notes, user recordings or secret analytics keys in commits or build artifacts.
7. Include `README.md` with one-command local setup, build/test commands, contributor flow and instructions for adding future questions. Include `DEPLOYMENT.md` with both root/subpath options and basic troubleshooting.

## 10. Quality assurance, accessibility, security and performance

Create and actually execute appropriate tests. At minimum:

### Source/content invariants (must PASS)

- Source parser finds **485** questions, **485 unique exact IDs**, **21** known topics and expected per-topic counts.
- 100% of original IDs have a corresponding page and correct, verbatim question text.
- No missing questions, invisible routes, empty topic, broken required content sections, missing metadata, invalid related IDs, malformed MDX or placeholder answers.
- Automated duplicate-content heuristics plus human/agent spot review per topic; investigate suspicious similarities rather than blindly trusting a passed count.
- A genuine index/readable coverage report generated from actual files (not copied from the source table).
- **No fake sources**: link existence can be mechanically checked where internet permits; relevance to claim must be reviewed.
- Kotlin code examples compile/test in a small dedicated JVM/Android sample harness wherever feasible; otherwise carefully mark conceptual snippets and provide all necessary context, not imaginary production-ready claims.

### Functionality tests

- Topic→question navigation and deep links; reload under a GitHub Pages base path; prev/next/related navigation.
- Search by exact ID, English technical term and Arabic term; filtering/sorting combinations and empty-result UX.
- Theme, Arabic RTL/English LTR, keyboard controls and mobile navigation.
- Bookmark, progress status, private note persistence across reloads, malformed storage fallback.
- Spaced repetition schedule, Again/Hard/Good/Easy, timezone boundaries, overdue handling.
- Mock interview selection, timer, hidden answers, interruption/reload handling, session recap.
- Export/import, invalid JSON rejection, schema version, user confirmation for reset.
- If implemented, microphone permission denial/unsupported browser, recording, playback and privacy handling.
- 404 and safe rendering of unusual question strings, code and special characters.

### Release quality gates

- Production build and typechecking pass on fresh install from a lockfile.
- No broken production routes, JS console errors on core journeys or persistent-state regressions.
- Confirm RTL layout and LTR code on representative phone screens; do at least one mobile-size visual pass.
- Reasonable page weight; avoid hydrating all 485 answers at once. Static pages/index must scale.
- Run automated accessibility checks where feasible and fix significant findings, including keyboard navigation and focus.
- Check basic security posture: no HTML injection through MDX/user notes, no exposed secrets, safe external links, no surprise data upload or hidden tracking.
- Build output includes sitemap/search artifacts and valid GitHub Pages paths.

### Suggested commands (adapt to real package scripts)

```bash
npm ci
npm run content:validate
npm run lint
npm run typecheck
npm run test
npm run build
npm run test:e2e
```

Do not falsely claim commands were run if tools were unavailable. Include actual exit statuses and relevant reports in the final verification.

## 11. Execution order — one continuous assignment, no midstream approvals

**Stage 0 — Audit:** inspect repo and input; verify 485/21 exact counts and source IDs; identify existing work; create checkpoints.

**Stage 1 — Domain/content model:** implement schemas, deterministic source importer and coverage validator; preserve all question metadata and original wording.

**Stage 2 — Site and visual system:** build finished routing, dashboard, topic pages, responsive question UX, accessibility, RTL/LTR and search; ensure every original question is routable.

**Stage 3 — Real content, all topics:** author substantive bilingual educational material and three interview-answer depths as appropriate for all 485 canonical questions. Perform quality checks continually; audit official docs and corrected nuanced examples. No shortcuts or mass-produced generic answers.

**Stage 4 — Interactive study:** implement bookmarks, notes, progress, flashcards, scheduling, learning paths and export/import.

**Stage 5 — Practice:** build timed mock interviews, interview answer comparison rubric, scenario/code challenges and safe optional local audio recording.

**Stage 6 — Validation:** unit, integration, E2E, content link/ID validation, mobile/RTL audit, code sample checks and performance/accessibility fixes.

**Stage 7 — Deployment:** set up verified GitHub Pages build/CI configuration, publish if authorized, verify URL and all production subpaths.

**Stage 8 — Final audit and delivery:** prove counts and working journeys, supply a final structured release report. Repeat fixes until available checks pass. Do not stop after scaffolding or the first working page.

Work through stages **without asking the user to approve each phase**. Internal milestones, task lists, automated scripts and commits are encouraged. Treat this as one complete delivery objective.

## 12. Hard acceptance criteria: definition of DONE

The project is only "complete" if ALL of the following are true:

- [ ] Actual supplied source parsed; 485 unique questions across 21 topics, original source IDs and English wording preserved.
- [ ] 485 distinct, valid, accessible question routes; each contains a genuine Arabic explanation, English short/structured answer, relevant Why/How, failure/trade-off analysis, production insight and a usable self-check.
- [ ] All 21 topic pages have correct groups/counts; five phases and at least a few curated learning paths work.
- [ ] Senior-level content is technically sound; current sensitive APIs documented honestly; citations are real and relevant; no copy-paste filler/placeholder pages.
- [ ] Functional dashboard, full-text search, navigation, filters, bookmarking, personal notes, progress, review and spaced repetition.
- [ ] Usable mock interview with real timer, honest user-scored rubric and meaningful session results.
- [ ] Premium-feeling, accessible, mobile-first bilingual-direction design (Arabic explanation and English interview text).
- [ ] Works without paid backend and without user account. Export/import protects user progress; privacy is disclosed.
- [ ] Static GitHub Pages-compatible production build, correct `site/base`, repository workflow, setup and deployment docs.
- [ ] Automated content validation, unit tests, representative E2E tests, link verification and quality checks pass **as actually run**.
- [ ] Any existing Android Academy assets, valid questions, site configuration and user work preserved or migrated intentionally.
- [ ] Verified live GitHub Pages link **if publishing was authorized and successful**, otherwise a deploy-ready artifact with only explicitly stated external activation blockers.

**A site with all 485 imported questions but only 20 written explanations is NOT done. A beautiful UI with sample content is NOT done. A green build with generic repetitive answers is NOT done. A locally working site with broken GitHub Pages base paths is NOT done.**

## 13. Mandatory final response from the implementing agent

Return one concise, evidence-based delivery report with these exact sections:

1. **Outcome:** what is complete and what is not, with no misleading claims.
2. **Repository / branch / commit:** exact identifiers if available.
3. **Live URL:** a verified URL if deployed; otherwise `Not deployed` and the precise access/settings limitation.
4. **Source fidelity:** `source IDs found`, `unique IDs`, `topics`, `question pages generated`, `fully reviewed content pages`, `questions missing`, `broken links`, `placeholder count` — all from actual scripts.
5. **Implemented capabilities:** dashboard, explanation/answers, code, search, SRS, mock interview, notes, recording if implemented, export/import, responsive, RTL/LTR.
6. **Quality gate table:** command, pass/fail, short evidence or logs; mention environment limitations explicitly.
7. **Technical decisions:** framework versions and any justified departures from this prompt.
8. **How to run locally:** exact commands and directory.
9. **How to publish/update:** exact GitHub Pages workflow and any one-time setting required.
10. **Remaining blockers or limitations:** only genuine blockers; include a deterministic resume command/checkpoint for anything constrained by external limits.

## 14. Final instruction — act now

Start by opening the repository and both the source bank and any previous academy materials. Audit, implement, populate **every question**, run checks, fix failures, then publish if permission exists. Be thoughtful about content accuracy and product polish. Do not ask the user to choose routine technologies, do not create a hollow demo, do not pause after a small portion and ask whether to continue, and **never confuse a content counter with real educational quality**.

**Your definition of success is a genuinely usable, complete Senior Android interview learning website that the owner could share publicly with confidence.**
