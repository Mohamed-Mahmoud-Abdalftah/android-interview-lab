---
id: "CIC-15"
question: "What Git conflicts can a revert of an older commit cause?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "B"
phase: 4
priority: "P2"
order: 434
editorial_status: "reviewed"
---

# CIC-15

## Original interview question

What Git conflicts can a revert of an older commit cause?

## What the interviewer evaluates

- Textual and semantic conflicts when reverting an old commit.
- Merge revert and deployed-state risks.

## Explanation in Arabic

ما هي تعارضات Git (Conflicts) التي يمكن أن يسببها التراجع عن كوميت قديم (`git revert`)، وكيف يتم حلها؟

1. طبيعة التعارض عند عمل Revert لكوميت قديم:
   - عندما تقوم بعمل `git revert` لكوميت حدث منذ أسابيع (مثلاً قبل 30 كوميت)، فإن Git يحاول تطبيق **عكس التغيير (Inverse Patch)** بدقة على الكود الحالي.
   - إذا كانت الكوميتات التي تلت ذلك الكوميت قد عدلت نفس الأسطر، أو غيرت أسماء الكلاسات أو الحزم (Refactoring)، أو حذفت الملف الأصلي، فإن Git لن يستطيع تطبيق التراجع آلياً وسيتوقف معلناً عن **Merge Conflict**.

2. أنواع التعارضات الشائعة:
   - **1. تعارضات نصية مباشرة (Content Conflicts)**: الكود المحذوف تم تعديل أسطره لاحقاً بواسطة ميزات أخرى. تظهر علامات التعارض القياسية (`<<<<<<< HEAD`, `=======`, `>>>>>>>`).
   - **2. تعارضات حذف ونقل الملفات (Tree / Rename Conflicts)**: الكوميت القديم أنشأ ملفاً، وكوميت لاحق نقله إلى مجلد آخر أو حذفه، فيحتار Git في كيفية عكس التغيير.
   - **3. تعارضات دلالية غير مرئية (Semantic / Compile Conflicts)**: أخطر نوع! قد ينجح الـ Revert دون أي تضارب نصي في Git، ولكن الكود لا يجمع (Compilation Error) أو يسبب كراش وقت التشغيل لأن دوال أخرى في النظام أصبحت تعتمد على وجود الكلاسات أو الـ APIs التي قمت بالتراجع عنها!

3. خطوات الحل الهندسي:
   - حل التعارضات النصية يدوياً في الملفات.
   - تشغيل `./gradlew compileDebugKotlin` و `./gradlew testDebugUnitTest` فوراً قبل إتمام الـ commit للتأكد من السلامة الدلالية للـ Revert.

## Practical walkthrough

خطوات حل تعارض ناتج عن revert لكوميت قديم بالخطوات والأوامر:
```bash
# 1. محاولة التراجع عن كوميت قديم:
git revert 3c7a10f
# المخرجات:
# error: could not revert 3c7a10f... feat: add loyalty reward engine
# hint: after resolving the conflicts, mark the corrected paths with 'git add <paths>'

# 2. فحص الملفات المتعارضة:
git status # يوضح: both modified: app/src/main/java/com/app/CheckoutViewModel.kt

# 3. فتح الملف وحل علامات التعارض النصية:
# إزالة أسطر الـ loyalty engine مع الإبقاء على تعديلات الدفع الجديدة بأمان

# 4. التحقق الحاسم من سلامة التجميع والاختبارات:
./gradlew compileDebugKotlin testDebugUnitTest

# 5. استكمال الـ Revert بعد نجاح التجميع:
git add app/src/main/java/com/app/CheckoutViewModel.kt
git revert --continue
git push origin main
```

## Why it matters and how it works

Git merges inverse changes into present tree, not the historical tree at the old commit. Conflict resolution needs understanding of later edits and dependencies. Tests of current combined state are necessary even if revert applies cleanly.

## Worked example

Commit A adds payment status `UNKNOWN`; B later adds UI handling. Reverting A alone may compile-fail or silently map unknown to declined. Review dependency graph, revert B too or fix-forward state machine, then test payment timeout and recovery.

## Trade-offs and decision criteria

Reverting is collaboration-safe for shared history, but can require a series of coordinated commits. Reset avoids patch conflicts only by rewriting history, which is unsafe for shared release branch and does not undo deployed side effects.

## Failure modes

Auto-resolving conflict with “ours” may leave half-reverted logic. Review tests and schema migrations, check backend compatibility and release artifact behavior.

## Production perspective

Hotfix PR includes conflict rationale, affected tests, data migration plan and rollout monitoring. Preserve source-to-artifact traceability.

## Interview answer — short

Reverting an older commit causes content conflicts when subsequent commits modified the same lines, tree conflicts if files were moved or deleted, and silent semantic conflicts where dependent code breaks at compile-time. Resolve them by manually reconciling diffs, running full compilation and unit tests, and finalizing with git revert --continue.

## Interview answer — structured

When executing `git revert` on an older commit, Git applies an inverse patch against current HEAD. This produces three distinct conflict categories:

1. **Content Conflicts (Direct Textual Invalidation)**:
   - Occurs when intermediate commits modified, refactored, or formatted the exact lines that the inverse patch attempts to delete or restore. Git halts with standard conflict markers (`<<<<<<< HEAD` vs `>>>>>>> parent of...`).

2. **Tree / Rename Conflicts**:
   - Arise when files created or modified by the old commit were subsequently renamed, moved to new packages during architectural modularization, or deleted entirely.

3. **Silent Semantic / Compilation Conflicts**:
   - The most insidious category: the inverse patch applies cleanly with zero textual conflicts, but subsequent commits introduced dependencies on classes, fields, or database schemas defined in the reverted commit. The codebase breaks during Kotlin compilation or triggers runtime exceptions.

Resolving an old revert mandates manually clearing conflict markers, followed by running `./gradlew compileDebugKotlin` and unit tests to verify semantic integrity before executing `git revert --continue`.

## Interview answer — deep senior

In large scale engineering teams, managing complex historical reverts requires operational discipline:

1. **The Revert Blast Radius Assessment**: Never blindly revert a 2-month-old commit in a production repo. Use `git log -S "SymbolName"` to identify every commit that touched or referenced the affected symbol since the target commit. If 15 subsequent features depend on it, an inverse patch will cause cascading fractures.

2. **Surgical Forward-Fix vs. Revert**: If an old commit introduced a bug but has deep architectural entanglement with current production code, executing `git revert` is often more dangerous than writing a targeted forward hotfix that neutralizes the buggy code path while preserving the surrounding public API contracts.

3. **Reverting a Long Chain**: If a feature comprised multiple commits, use range revert: `git revert OLDER_COMMIT..NEWER_COMMIT`. Git reverts them in reverse chronological order, minimizing intermediate dependency conflicts.

## How to answer in the interview

- **Why:** later commits can depend on older behavior.
- **How:** inspect graph, revert on branch, review current diff.
- **Trade-off:** broad revert versus narrow compensating fix.
- **Failure case:** clean apply creates semantic breakage.
- **Production solution:** test affected variants and migrations.

## Deep-dive talking points

Prompt for inverse patch, textual versus semantic conflicts, merge mainline and shipped migration.

## Follow-up questions

- **Interviewer:** "What is a semantic Git conflict and why is it dangerous in reverts?"
  **Answer:** "A conflict where code merges cleanly without textual errors, but breaks at compile or runtime because remaining code depended on symbols removed by the revert."

- **Interviewer:** "In what order does Git revert a range of commits (`git revert A..B`)?"
  **Answer:** "It reverts in reverse chronological order (from B backward to A) to cleanly unwind dependencies."

## Self-check rubric

Draw how a later commit can depend on lines changed by an older commit; predict the revert conflict, resolve the intended behavior and run targeted tests rather than assuming inverse patches commute.

## References and reviewed-on date

- [Git revert documentation](https://git-scm.com/docs/git-revert) — revert semantics.
- [Room migration guide](https://developer.android.com/training/data-storage/room/migrating-db-versions) — deployed schema effects.

Technically reviewed against primary documentation on 2026-10-13.
