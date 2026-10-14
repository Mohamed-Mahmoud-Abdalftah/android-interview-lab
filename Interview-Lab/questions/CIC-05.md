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

Git reset --soft moves HEAD back to a specified commit leaving both the Index and Working Directory intact, keeping changes staged. Git reset --mixed (the default) moves HEAD and resets the Index, leaving changes unstaged in the Working Tree. Git reset --hard resets HEAD, Index, and Working Tree, permanently discarding all changes.

## Interview answer — structured

The difference between Git reset modes lies in how they interact with Git's three trees (HEAD, the Index, and the Working Tree).

First, **`git reset --soft <commit>`**. Next, updates the HEAD ref pointer to the target commit.
Does NOT touch the Index (Staging area) or the Working Tree. All changes from the undone commits remain staged, ready to be immediately re-committed. Ideal for re-organizing commits or squashing local work.
**`git reset --mixed <commit>` (Default)**. Updates HEAD and resets the Index to match the target commit.
Leaves the Working Tree unmodified on disk. All changes remain intact in your files but appear as unstaged modifications. Useful for selectively re-staging files into atomic commits.
**`git reset --hard <commit>`**. Updates HEAD, resets the Index, and forces the Working Tree to match the target commit.
Completely obliterates all tracked modifications in the working directory. Finally, it is a destructive operation; uncommitted local work cannot be recovered.


## Interview answer — deep senior

From an operational safety and disaster recovery perspective, understanding reset boundaries is critical.

First, with Disaster Recovery via `git reflog, if a developer executes an accidental `git reset --hard HEAD~5` and loses committed work, the commits are not instantly wiped from Git's object database. As long as those commits were previously committed, their SHA identifiers exist in the local reference log. Running `git reflog`, identifying the previous commit hash, and running `git reset --hard <previous-sha>` fully restores the lost state. Next, with The Danger with Untracked Files, `git reset --hard` only affects files tracked by Git. Untracked files (new files never staged via `git add`) are left untouched on disk. To wipe both tracked and untracked artifacts, teams run `git clean -fd` alongside `git reset --hard`.
Finally, with CI Cleaning Best Practices, on self-hosted CI runners that reuse workspaces across pipeline runs, running `git reset --hard HEAD && git clean -ffdx` ensures a 100% clean, pristine workspace without residual build artifacts from previous builds.


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
