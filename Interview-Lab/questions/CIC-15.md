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

## Concept and technical explanation

Executing `git revert` on a historical commit creates an inverse patch designed to negate original changes, which often collides with subsequent evolutionary commits:
- Mechanisms of Historical Reverts:
  - Unlike `git reset`, which rewrites Git history, `git revert` generates a new commit that applies the inverse diff of the target commit against current HEAD.
  - When the reverted commit is weeks or months old, intermediate commits have built on, refactored, or renamed the affected code, creating complex conflict classes.
- Taxonomy of Revert Conflicts:
  - Textual Content Conflicts:
    - Occurs when intermediate commits modified the exact lines of code targeted for removal or restoration. Git halts with standard conflict markers (`<<<<<<< HEAD`, `=======`, `>>>>>>> parent of...`).
  - Tree and Rename Conflicts:
    - Arise when files created, edited, or deleted in the target commit were subsequently relocated during package refactoring, renamed, or deleted. Git cannot determine where to apply the inverse patch.
  - Silent Semantic and Compilation Conflicts (The Most Dangerous Class):
    - The inverse patch applies cleanly with zero textual conflicts, yet breaks the build. This occurs when subsequent features rely on public interfaces, Room entities, or DI bindings introduced in the reverted commit. The codebase breaks during Kotlin compilation (`compileDebugKotlin`) or triggers runtime `NoSuchMethodError` crashes.
  - Reverting Merge Commits (`git revert -m 1`):
    - Reverting a merge commit reverses the code changes but does NOT undo the Git history. Subsequent attempts to re-merge the original branch will be treated as already merged, silently omitting all branch changes unless the revert itself is reverted.

## Practical walkthrough (English)

Resolving a complex historical revert with verification checks:
```bash
# 1. Attempt historical revert
git revert 4a8f10b
# Output:
# error: could not revert 4a8f10b... feat: add loyalty cashback engine
# hint: after resolving the conflicts, mark the corrected paths with 'git add <paths>'

# 2. Inspect conflict state
git status
# Unmerged paths:
#   both modified:   feature/cart/src/main/java/com/company/CartViewModel.kt

# 3. Resolve conflict markers manually in IDE, removing loyalty hooks while preserving cart logic

# 4. Mandatory Semantic Verification: Ensure project compiles and passes unit tests
./gradlew compileDebugKotlin testDebugUnitTest

# 5. Finalize the revert commit
git add feature/cart/src/main/java/com/company/CartViewModel.kt
git revert --continue

# 6. Push verified revert to remote mainline
git push origin main
```

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

Reverting an older commit causes textual conflicts when subsequent commits modified the same lines, tree conflicts when files were moved or deleted, and silent semantic conflicts where dependent code fails at compile-time despite clean Git patches. Resolve them by reconciling diffs manually, running compilation and unit tests to ensure semantic integrity, and completing with git revert continue.

## Interview answer — structured

Reverting an older commit introduces substantial integration risk because Git applies an inverse patch against current mainline code.
This operation frequently triggers three distinct conflict categories. Textual content conflicts emerge when intermediate commits modified or reformatted the exact lines being reverted, requiring manual resolution in the editor. Tree and rename conflicts arise when files were moved or deleted during module refactoring, leaving Git unable to locate the target path.
The most dangerous category is silent semantic conflict. In this scenario, the inverse patch applies without any textual Git conflicts, but the build fails because subsequent features depend on classes, methods, or database migrations introduced in the reverted commit.
To safely resolve historical reverts, engineers must manually clear conflict markers, run Kotlin compilation and JVM unit tests locally to verify semantic integrity, and only then finalize the revert using git revert continue.

## Interview answer — deep senior

From a software configuration management and platform safety perspective, reverting an older commit in a high-velocity Android repository is an invasive surgical operation.
The primary risk is assuming that a clean Git revert implies working software. Git operates on line deltas, entirely blind to Kotlin type systems or Android component lifecycles. A historical commit often acts as an architectural foundation for dozens of subsequent commits. When an engineer executes git revert on a commit from two months ago, the inverse patch may remove a Dagger module binding or an entity column. Even if the text patch applies cleanly, downstream code invoking that removed dependency will fail compilation or trigger catastrophic runtime crashes in production.
Furthermore, reverting merge commits introduces severe topological traps. Reverting a merge commit with the minus-m flag cancels the code diff but preserves the ancestor graph. If the feature team later fixes the issue on their original branch and attempts to merge it back into main, Git assumes the commits are already present and silently excludes all original changes. Resolving this requires re-reverting the revert commit before merging.
Therefore, our team policy mandates evaluating blast radius using git log before reverting. If historical entanglement is deep, we favor a forward hotfix that neutralizes the defective behavior behind a feature flag over a blind git revert, safeguarding the public API contract while mitigating production impact.

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
