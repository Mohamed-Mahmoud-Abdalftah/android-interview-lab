---
id: "CIC-05"
question: "Compare git reset --soft versus --hard."
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "A"
phase: 4
priority: "P2"
order: 424
editorial_status: "reviewed"
---

# CIC-05

## Original interview question

Compare git reset --soft versus --hard.

## What the interviewer evaluates

- Index/worktree effects of soft versus hard reset.
- Commit movement and data-loss boundary.

## Concept and technical explanation

Understanding Git reset variants requires analyzing how they manipulate Git's three fundamental architecture trees:
- Git's Three Trees:
  1. HEAD: Pointer tracking the latest commit snapshot of the current branch.
  2. Index (Staging Area): The proposed next commit snapshot prepared via git add.
  3. Working Tree: The active filesystem directory containing files on disk.
- Reset Modes Comparison:
  - git reset --soft <commit>:
    * Updates the HEAD reference to point to the designated commit.
    * Leaves both the Index and the Working Tree completely untouched.
    * Result: All changes introduced after that commit remain staged in the Index, ready to be immediately re-committed. Ideal for amending messages, combining local commits, or restructuring history before pushing.
  - git reset --mixed <commit> (Default behavior):
    * Updates HEAD and resets the Index to match the target commit snapshot.
    * Leaves the Working Tree files on disk untouched.
    * Result: Undone changes remain intact in your files but become unstaged modifications. Ideal for splitting commits or re-staging files selectively.
  - git reset --hard <commit>:
    * Updates HEAD, resets the Index, and forces the Working Tree to match the target commit snapshot.
    * Destructive Operation: Obliterates all tracked changes in files on disk. Uncommitted changes cannot be recovered.
- Disaster Recovery via Reflog:
  - If a commit was previously committed, git reflog retains its SHA identifier. Running git reset --hard <previous-sha> safely recovers lost commits.

## Practical walkthrough (English)

Hands-on CLI scenarios comparing soft, mixed, and hard resets:
```bash
# Scenario 1: Undo accidental commit, preserve changes as staged to edit commit message:
git commit -m "wip payment featur"
git reset --soft HEAD~1
git status # Shows: Changes to be committed (Staged)
git commit -m "feat(payment): integrate biometric confirmation"

# Scenario 2: Split last commit into two atomic commits (Default Mixed Reset):
git reset --mixed HEAD~1
git status # Shows: Changes not staged for commit
git add PaymentService.kt && git commit -m "feat: add payment service"
git add PaymentTest.kt && git commit -m "test: add payment unit tests"

# Scenario 3: Discard bad experiment completely and restore clean main branch state:
git reset --hard origin/main

# Scenario 4: Disaster recovery after accidental hard reset using git reflog:
git reflog # Locate commit SHA before the reset, e.g. 7c8d9e0
git reset --hard 7c8d9e0 # Restores lost commits completely!
```

## Explanation in Arabic

قارن بين `git reset --soft` و `git reset --hard` (بالإضافة إلى `--mixed`) وماذا يحدث للـ HEAD والـ Index وبيئة العمل؟

1. شجرة Git الثلاثية (The Three Trees):
   - **HEAD**: مؤشر آخر commit تم تسجيله.
   - **Index (Staging Area)**: الملفات المجهزة للـ commit القادم (`git add`).
   - **Working Tree (Working Directory)**: الملفات الموجودة حالياً على قرصك الصلب داخل مجلد المشروع.

2. المقارنة التفصيلية بين أنواع الـ Reset:
   - **`git reset --soft <commit>`**:
     * يحرك مؤشر HEAD فقط إلى الكوميت المحدد.
     * **يترك الـ Index والـ Working Tree كما هما تماماً**.
     * النتيجة: كل التغييرات التي حدثت بعد هذا الكوميت تظل في حالة **Staged** (مجهزة للكوميت)، ممتازة جداً إذا أردت تعديل رسالة الكوميت أو دمج آخر 3 كوميتات محلياً.
   - **`git reset --mixed <commit>` (الوضع الافتراضي)**:
     * يحرك HEAD ويعيد تعيين الـ Index ليطابق الكوميت.
     * **يترك الـ Working Tree سليمة**.
     * النتيجة: التغييرات تظل موجودة في ملفاتك ولكنها تصبح **Unstaged** (غير مجهزة).
   - **`git reset --hard <commit>`**:
     * يحرك HEAD ويعيد تعيين الـ Index ويعيد تعيين الـ Working Tree!
     * **يمسح كل التغييرات غير المسجلة تماماً من على القرص**.
     * أمر تدميري (Destructive): لا يُستخدم إلا إذا كنت متأكداً بنسبة 100% أنك تريد التخلص من كل ما قمت به والعودة لتلك النقطة في الزمن.

## Practical walkthrough

سيناريوهات عملية توضح متى تستخدم كل نوع من الـ Reset:
```bash
# سيناريو 1: قمت بعمل commit لرسالة خاطئة وتريد إعادة تجهيز الكود مع تعديل بسيط:
git commit -m "wip featur"
git reset --soft HEAD~1
# الآن كل الملفات ما زالت في الـ Staging Area:
git status # shows: Changes to be committed
git commit -m "feat(auth): implement biometric login challenge"

# سيناريو 2: قمت بعمل commit وأدركت أنك تريد فصل الملفات إلى كوميتين منفصلين:
git reset --mixed HEAD~1 # أو ببساطة git reset HEAD~1
git status # shows: Changes not staged for commit
git add UserAuth.kt && git commit -m "feat: add auth service"
git add UserAuthTest.kt && git commit -m "test: add auth unit tests"

# سيناريو 3: تجربة فاشلة تماماً وتريد مسح كل ما كتبته والعودة لفرع main النظيف:
git reset --hard origin/main
# تم مسح كل التعديلات غير المسجلة والمسجلة بعد origin/main!
```

## Why it matters and how it works

Reset moves the current branch ref (or HEAD). Soft leaves staged snapshots available for recommit. Hard writes target tree into index/worktree and discards tracked local changes; untracked files are a separate concern. Reflog may help recover commit objects but should not be a substitute for caution.

## Worked example

After two local experimental commits, use `git reset --soft HEAD~2` to combine changes into one reviewed commit. If abandoning a disposable local branch, `git reset --hard origin/main` is possible only after inspecting status and preserving anything needed.

## Trade-offs and decision criteria

Soft is useful for rewriting local commit boundaries. Hard can restore a known tree quickly but risks irreversible local loss and shared-branch divergence. Prefer revert for already published bad commits.

## Failure modes

Running hard reset in a dirty workspace loses tracked edits. Confirm `git status`, target SHA and branch before executing; use a backup/stash when appropriate. Do not assume reset deletes untracked build files.

## Production perspective

Team rules protect main from force-push and document recovery with reflog. CI release artifacts always point to immutable commit SHA.

## Interview answer — short

Git reset --soft moves the HEAD pointer to a target commit while keeping both the Index and Working Tree intact, leaving changes staged for a new commit. Git reset --mixed moves HEAD and resets the Index, leaving changes unstaged on disk. Git reset --hard resets HEAD, Index, and Working Tree, permanently discarding all tracked changes.

## Interview answer — structured

The difference between Git reset modes lies in how they interact with Git's three fundamental architecture trees: the HEAD pointer, the Index staging area, and the Working Tree.
When executing git reset --soft, Git moves the HEAD pointer backward to the specified commit, but leaves both the Index and the Working Tree unmodified. As a result, all modifications from the undone commits remain staged, making it the ideal command for amending commit messages, adding missing files, or squashing recent commits locally before opening a pull request.
In contrast, git reset --mixed, which is the default reset mode, moves HEAD and clears the Index to match the target commit, but leaves your Working Tree files untouched on disk. The modifications become unstaged, allowing developers to review differences and re-stage them into smaller, atomic commits.
Finally, git reset --hard is a destructive operation that updates HEAD, resets the Index, and forces the Working Tree files to match the target commit, completely obliterating uncommitted changes. However, if committed work was accidentally wiped, it can be recovered using git reflog.

## Interview answer — deep senior

From a version control architecture and developer safety perspective, mastering reset mechanics prevents catastrophic data loss and clarifies workspace synchronization.
Git manages data across three decoupled layers: HEAD records the committed object graph, the Index stages tree objects for the next snapshot, and the Working Tree holds the local OS filesystem state. Understanding how reset flags boundary these layers enables surgical local modifications without fear.
Using git reset --soft HEAD~1 is the cleanest method to rewrite local commit history. It rolls back the branch pointer while preserving all edited files in the staging area. This allows engineers to split, combine, or re-label commits before publishing.
When employing git reset --hard, engineers must understand what is recoverable and what is lost forever. If modifications were previously committed, Git's content-addressable object store retains the commit objects even after the branch pointer moves away. Running git reflog exposes the history of HEAD movements, allowing developers to locate the orphaned commit SHA and restore it via git reset --hard <sha>. However, if a developer had uncommitted, untracked, or dirty working tree changes when executing git reset --hard, those uncommitted diffs never existed in Git's object database and are destroyed permanently.
Furthermore, git reset --hard only alters tracked files; newly created untracked files are ignored. In continuous integration runners where clean state is mandatory between builds, teams run git reset --hard HEAD followed by git clean -ffdx to purge untracked files, ignored compiler caches, and build outputs.

## How to answer in the interview

- **Why:** reset changes which work is retained.
- **How:** name HEAD, index and working-tree effects.
- **Trade-off:** local cleanup versus loss of work.
- **Failure case:** hard reset discards tracked edits.
- **Production solution:** inspect status and use revert for shared history.

## Deep-dive talking points

Prompt for three trees, staged result, tracked loss, untracked caveat and shared history.

## Follow-up questions

- **Interviewer:** "Can you recover commits lost after an accidental `git reset --hard`?"
  **Answer:** "Yes, using `git reflog` to locate the commit hash before the reset and running `git reset --hard <sha>`."

- **Interviewer:** "What is the primary use case for `git reset --soft HEAD~1`?"
  **Answer:** "Undoing the last commit while keeping all changes staged to rewrite the commit message or add missing files."

## Self-check rubric

Given three local commits, predict HEAD, index and working tree after reset --soft versus --hard. Explain why a hard reset on a shared branch can discard work and confuse collaborators.

## References and reviewed-on date

- [Git reset documentation](https://git-scm.com/docs/git-reset) — mode effects.
- [Android app publishing](https://developer.android.com/studio/publish) — released artifact context.

Technically reviewed against primary documentation on 2026-10-13.
