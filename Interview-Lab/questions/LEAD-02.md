---
id: "LEAD-02"
question: "How do you review code for correctness, security, readability, and testability?"
topic: "Senior Ownership, Communication & Technical Leadership"
code: "LEAD"
group: "A"
phase: 5
priority: "P2"
order: 457
editorial_status: "reviewed"
---

# LEAD-02

## Original interview question

How do you review code for correctness, security, readability, and testability?

## What the interviewer evaluates

- Risk-ranked code review with constructive, verifiable feedback.
- Correctness/security before style and testability.

## Explanation in Arabic

كيف تدير عملية مراجعة الكود (Code Review) بشكل منهجي يغطي الصحة البرمجية (Correctness)، والأمان (Security)، وسهولة القراءة، وقابلية الاختبار؟

1. فلسفة مراجعة الكود للـ Senior Engineer:
   - مراجعة الكود ليست تصيداً للأخطاء الشخصية، بل هي **بوابة جودة هندسية (Quality Gate) وأداة لنشر المعرفة داخل الفريق**.
   - **أتمتة ما يمكن أتمتته**: لا تضيع وقتك البشري في مراجعة المسافات والتنسيق؛ دع Spotless و ktlint و Detekt يرفضون الـ PR آلياً.

2. المحاور الأربعة للمراجعة العميقة:
   - **1. الصحة البرمجية ومنطق العمل (Correctness)**: هل الكود يلبي متطلبات الـ User Story؟ هل تم التعامل مع الحالات الحدية (Empty states, Network timeout, Screen rotation, Process Death)؟ هل هناك تسريبات ذاكرة أو Coroutine leaks؟
   - **2. الأمان والخصوصية (Security)**: هل تم تشفير البيانات الحساسة؟ هل تم منع كشف الـ Tokens في الـ Logs؟ هل يوجد فحص لمدخلات الـ Deep Links؟ هل تم تعيين `android:exported="false"` للمكونات غير العامة؟
   - **3. سهولة القراءة والمعمارية (Readability & Architecture)**: هل الكود يتبع النمط المعتمد (MVI/MVVM)؟ هل التسميات تعبر عن نية الكود (Intent-revealing names)؟ هل تم احترام Single Responsibility Principle؟
   - **4. قابلية الاختبار وجودة الفحص (Testability)**: هل الكود الجديد مغطى بـ Unit Tests حقيقية تفحص منطق العمل وليس مجرد رفع نسبة التغطية (Code Coverage) بسطور وهمية؟

## Practical walkthrough

قائمة مراجعة عملية (Code Review Checklist) ونموذج للتعليقات البناءة:
```markdown
### ❌ نموذج تعليق سيئ وغير بناء:
"This is wrong. Change it to Coroutines and fix your architecture."

### ✅ نموذج تعليق Senior بناء وتعليمي:
"[Blocking - Correctness]: I noticed we're collecting this Flow directly inside `onCreate`:
`viewModel.state.collect { ... }`
On Android, if the app goes to the background, this coroutine continues emitting,
which can trigger UI updates and waste battery or crash if accessing views.
Could we wrap this in `repeatOnLifecycle(Lifecycle.State.STARTED)`?
Here's the official Android guide for reference: [link]"

### مستويات تصنيف الملاحظات (Conventional Comments):
- **[Blocking]**: خطأ منطقي، تسريب ذاكرة، ثغرة أمنية (يمنع الدمج).
- **[Non-blocking / Suggestion]**: تحسين أداء طفيف أو إعادة صياغة بديلة.
- **[Question]**: طلب توضيح حول قرار معين.
- **[Nitpick]**: تفصيلة جمالية غير مؤثرة (لا تمنع الدمج إطلاقاً).
- **[Praise]**: إشادة بحل هندسي ذكي ومكتوب باحترافية.
```

## Why it matters and how it works

Review is a risk filter and a knowledge-sharing process. Check source of truth, lifecycle, concurrency, security boundary, performance and test evidence. Different findings have different severity; blocking comments should identify a real defect or unmet requirement.

## Worked example

On a PR that retries a charge after timeout, ask whether the same operation ID is persisted before send and enforced server-side. Request a lost-response test. A style issue on the same PR can be nonblocking if formatter handles it.

## Trade-offs and decision criteria

Deep reviews take time; risk-based sampling focuses attention. Automated lint handles routine formatting, freeing human review for logic and threat models. Excessive nitpicks can slow delivery and discourage discussion.

## Failure modes

Approving because tests pass misses untested trust boundaries. Blocking on personal naming taste wastes attention. Separate required change from suggestion and cite the concrete failure mode.

## Production perspective

Team review checklist includes release variant, data migration, API contract, telemetry redaction and rollback for risky code. Measure defect escapes and review latency, not comment count.

## Interview answer — short

Review code systematically by automating style and formatting via linters, focusing human review on business correctness, edge cases, memory leaks, security vulnerabilities, architectural alignment, and meaningful unit test coverage. Use conventional comment prefixes (Blocking, Non-blocking, Nitpick) to communicate intent constructively.

## Interview answer — structured

A structured code review process balances technical rigor with psychological safety and team velocity.

First, **Automate Mechanical Checks**. Next, enforce formatting (Spotless/ktlint), static analysis (Detekt), and framework issues (Android Lint) in automated CI gates. Human reviewers should never spend time debating tab widths or unused imports.
**Four-Pillar Review Rubric**. With Correctness, validate business logic fidelity, edge cases (empty states, process death, offline states), coroutine lifecycle safety (`repeatOnLifecycle`), and thread-safety.
With Security, inspect sensitive data storage (EncryptedSharedPreferences), log sanitization (no PII in Logcat), secure component exports (`android:exported`), and deep-link payload validation. With Architecture & Maintainability, ensure separation of concerns, adherence to team architectural boundaries (Clean Architecture / MVI), and clear domain naming.
With Testability, verify that new code introduces robust unit tests verifying behavior and edge cases rather than tautological mock assertions. **Empathetic and Actionable Feedback**.
Finally, use structured conventional prefixes: `[Blocking]`, `[Suggestion]`, `[Question]`, `[Nitpick]`. Provide clear technical rationale and links to official documentation rather than subjective directives.


## Interview answer — deep senior

From an engineering leadership and team velocity standpoint, code reviews require operational governance.

First, with PR Size Caps and Review Latency SLA, research proves review thoroughness drops precipitously on PRs exceeding 400 lines of code. Enforce a team cultural limit: PRs should be small and atomic ($< 300$ lines). Establish an internal SLA where PRs are reviewed within 4 business hours to avoid blocking teammates. Next, with Pairing on Complex Architecture, when reviewing foundational changes (e.g. Migrating authentication engines or introducing a new database schema), asynchronous GitHub comments are inefficient and lead to misunderstandings. Senior leads jump on a 15-minute synchronous pairing session to align on the mental model before final sign-off.
Finally, with Fostering Codebase Collective Ownership, use reviews to mentor engineers and highlight great work with explicit `[Praise]` comments. Encourage junior engineers to review senior PRs; asking questions on unfamiliar patterns democratizes architectural knowledge across the squad.


## How to answer in the interview

- **Why:** review prevents escaped behavior and boundary errors.
- **How:** follow contract, security, clarity and test evidence.
- **Trade-off:** review depth versus release speed.
- **Failure case:** style nit hides an unsafe retry.
- **Production solution:** block on demonstrated risk and verify fix.

## Deep-dive talking points

Prompt for severity, trust boundary, targeted test, respectful feedback and rollback.

## Follow-up questions

- **Interviewer:** "Why should formatting and linting checks be completely removed from human code reviews?"
  **Answer:** "Because automated CI linters execute them instantaneously and objectively, freeing human reviewers to focus on architectural correctness and security."

- **Interviewer:** "What is the benefit of using prefixes like `[Blocking]` and `[Nitpick]` in review comments?"
  **Answer:** "It provides unambiguous clarity to the PR author on which comments require resolution before merge versus which are purely optional suggestions."

## Self-check rubric

Review correctness, security boundaries, readability and testability with one concrete PR example; distinguish a blocking invariant from a style preference and propose a verifiable fix.

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — design boundaries.
- [Google code review guidance](https://google.github.io/eng-practices/review/reviewer/) — primary review process guidance.

Technically reviewed against primary documentation on 2026-10-13.
