---
id: "CIC-07"
question: "What are git stash, cherry-pick, and fork?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "A"
phase: 4
priority: "P2"
order: 426
editorial_status: "reviewed"
---

# CIC-07

## Original interview question

What are git stash, cherry-pick, and fork?

## What the interviewer evaluates

- Stash, cherry-pick and fork as distinct collaboration tools.
- Conflict and provenance trade-offs.

## Concept and technical explanation

Advanced Git mechanisms solve context switching, isolated patch backporting, and decentralized contribution boundaries:
- Detailed Breakdown of Operations:
  1. git stash:
     - Shelves uncommitted modifications (both staged and unstaged files) into an internal LIFO stack (stash@{0}), resetting the Working Tree to match the clean HEAD commit.
     - Primary Use Case: Urgent context switching (e.g. investigating an immediate production crash on another branch while midway through feature development).
     - Essential Flag: git stash -u (or --include-untracked) to ensure newly added, untracked files are captured alongside tracked edits.
     - Volatility Risk: Stashes are strictly local and unbacked; leaving large refactors in stash risks unrecoverable data loss during machine failure.
  2. git cherry-pick <commit-sha>:
     - Extracts the precise diff introduced by a designated commit on any branch and applies it as a brand-new commit on the currently active branch.
     - Primary Use Case: Hotfix backporting (e.g. applying an emergency security patch committed to main onto an active release/2.4 maintenance branch without merging unready features).
     - Best Practice: Use git cherry-pick -x to append origin commit metadata and preserve auditability.
  3. Fork:
     - A server-side clone of a remote repository hosted under an independent user or organization account on GitHub/GitLab.
     - Primary Use Case: Open-source collaboration and enterprise contractor boundaries where external contributors lack direct write permissions and submit contributions via pull requests across forks.

## Practical walkthrough (English)

Hands-on CLI usage for stash, cherry-pick, and fork synchronization:
```bash
# 1. Stash dirty workspace including untracked files with a descriptive message:
git stash push -u -m "WIP: biometric card tokenization"
git checkout hotfix/crash-fix
# ... resolve hotfix, commit, and push ...
git checkout feature/biometric
git stash pop # Restores files and removes them from the stash stack

# 2. Backport a hotfix commit from main to release-v1.4 using cherry-pick:
git checkout release/v1.4
git log origin/main --oneline -n 3 # Locate target commit SHA, e.g. c8d9e0f
git cherry-pick -x c8d9e0f # -x records original commit hash in commit message
git push origin release/v1.4

# 3. Synchronize a local fork with upstream canonical repository:
git remote add upstream https://github.com/organization/android-core.git
git fetch upstream
git checkout main
git merge upstream/main
```

## Explanation in Arabic

ما هي أدوات Git المتقدمة: `git stash`، و `git cherry-pick`، ومفهوم الـ Fork، ومتى يُستخدم كل منها؟

1. تخزين العمل المؤقت (`git stash`):
   - يقوم بحفظ التغييرات غير المسجلة مؤقتاً في Stash Stack وتفريغ الـ Working Tree لتعود نظيفة.
   - متى يُستخدم؟ عندما تكون في منتصف ميزة وتطلب منك القيادة فجأة إصلاح خطأ طارئ (Hotfix) على فرع آخر، أو عندما تريد عمل `git pull` ولكن تغييراتك المحلية تمنع ذلك.
   - ملاحظة هامة: `git stash` الافتراضي يخزن الملفات المعدلة المسجلة فقط؛ لتخزين الملفات الجديدة غير المسجلة (Untracked) يجب استخدام `git stash -u`.

2. انتقاء الكوميتات (`git cherry-pick`):
   - يتيح لك أخذ commit محدد بالـ hash بتاعه من فرع معين، وإعادة تطبيقه فقط دون بقية الفرع على فرعك الحالي.
   - متى يُستخدم؟ في سيناريو الـ Backporting: إصلاح Bug على فرع التطوير `main` وتريد تطبيق نفس الإصلاح على فرع الإنتاج القديم `release/2.4` دون سحب ميزات `main` غير الجاهزة.

3. التفريع المستقل (Fork):
   - استنساخ كامل للمستودع على مستوى السيرفر (GitHub/GitLab) تحت حسابك الشخصي أو منظمة منفصلة.
   - متى يُستخدم؟ في مشاريع الـ Open Source والمكتبات الخارجية (Libraries)، أو عندما لا يملك المطور صلاحيات الكتابة (Push) على المستودع الأصلي، فيقوم بعمل Fork ورفع التغييرات إليه ثم فتح Pull Request للمستودع الأصلي (Upstream).

## Practical walkthrough

أمثلة لأوامر `stash` و `cherry-pick` الشائعة في بيئة العمل اليومية:
```bash
# 1. استخدام git stash مع الملفات غير المتابعة (untracked files):
git stash push -u -m "WIP: payment card validation logic"
git checkout hotfix/crash-fix
# ... إصلاح العطل ورفعه ...
git checkout feature/payment
git stash pop # استعادة التغييرات ومسحها من الـ stash stack

# 2. استخدام cherry-pick لنقل إصلاح أمني من main إلى فرع الإصدار release-v1.4:
git checkout release/v1.4
git log origin/main --oneline -n 3 # العثور على الكوميت المطلوب، e.g., c8d9e0f
git cherry-pick c8d9e0f
git push origin release/v1.4

# 3. مزامنة الـ Fork المحلي مع المستودع الأصلي (Upstream):
git remote add upstream https://github.com/original-org/android-core.git
git fetch upstream
git checkout main
git merge upstream/main
```

## Why it matters and how it works

Stash entries are local refs and can conflict when reapplied. Cherry-pick replays a patch and creates a different commit hash, so repeated picks can duplicate logical changes. A fork is a repository-level collaboration boundary, not a Git command that synchronizes automatically.

## Worked example

Interrupt feature work for production fix: stash uncommitted edits, branch from release, apply a reviewed hotfix, cherry-pick it to main if needed, then return and apply stash with conflict review. For external contributor, use fork/PR without granting write access.

## Trade-offs and decision criteria

Stash is convenient but easy to forget; a temporary commit/branch is safer for longer work. Cherry-pick is surgical but can fragment history and miss dependencies. Fork limits permissions but adds upstream-sync work.

## Failure modes

Cherry-picking only one of two dependent commits produces a broken build. Inspect dependencies and run tests. Applying a stale stash can conflict or reintroduce outdated code; review the diff.

## Production perspective

Team hotfix runbook specifies source branch, target branches and mapping between original/cherry-picked SHA. External PRs run without signing secrets.

## Interview answer — short

Git stash shelves uncommitted changes to allow clean branch switching for urgent tasks. Git cherry-pick extracts and applies a specific commit by hash from another branch onto the current branch without merging the full branch. A Fork is a server-side repository copy enabling external contributors to propose changes via pull requests without direct push access.

## Interview answer — structured

These three Git tools solve distinct workflow isolation and collaboration challenges across engineering teams.
Git stash temporarily shelves uncommitted local modifications, both staged and unstaged, onto an internal stack and resets the working directory to clean HEAD. It is essential for rapid context switching, such as interrupting feature development to investigate an emergency hotfix. Using the include-untracked flag guarantees newly created files are also preserved.
Git cherry-pick extracts the exact diff from a designated commit on another branch and applies it as a brand-new commit on the current branch. It is primarily used for backporting bug fixes from the main trunk onto active release or maintenance branches without pulling in unreleased features.
A Fork is a server-side clone of a repository created under an independent user or organization account on platforms like GitHub. It provides a clean security boundary for open-source projects and external contractors who lack direct repository write permissions, allowing them to push changes to their fork and submit cross-repository pull requests to the upstream repository.

## Interview answer — deep senior

From a version control governance and release engineering perspective, stash, cherry-pick, and forks introduce operational nuances that require disciplined usage.
While git stash is convenient for short context switches, treating it as a long-term storage mechanism is dangerous. Stashes reside exclusively on the developer's local hard drive and are not backed up to remote servers. If a machine crashes or a developer runs hard clean commands, uncommitted stashed work can be lost forever. Mature teams establish a convention where multi-day exploratory work is committed and pushed to a remote draft branch rather than parked in a local stash.
When executing git cherry-pick, senior engineers guard against duplicate commit hazards. Applying a commit from main onto a release branch creates an identical diff with a distinct SHA hash. If that release branch is eventually merged back into main, Git must reconcile two commits sharing identical code changes, which can trigger confusing conflict resolutions. We always execute git cherry-pick with the -x flag, which automatically appends a reference to the source commit SHA in the commit message, preserving provenance and simplifying future release auditing.
Finally, managing forked workflows at scale requires automated upstream synchronization. In large organizations utilizing vendor forks, drift between the internal fork and upstream repositories quickly compounds into painful merge conflicts. Teams configure automated scheduled workflows that fetch upstream changes and rebase internal tracks continuously, ensuring external dependencies and forks remain closely aligned with the canonical codebase.

## How to answer in the interview

- **Why:** context switching and branch transfer have different needs.
- **How:** stash local state, cherry-pick a commit, fork a repository.
- **Trade-off:** selective patch speed versus dependency risk.
- **Failure case:** hotfix lacks its paired migration.
- **Production solution:** review destination diff and run its tests.

## Deep-dive talking points

Prompt for local versus repo scope, new commit SHA, dependent commits, fork PR secret boundary.

## Follow-up questions

- **Interviewer:** "Why should you use the `-x` flag when cherry-picking commits?"
  **Answer:** "It automatically records the original commit SHA in the commit message, preserving provenance and simplifying future auditability."

- **Interviewer:** "What is the difference between `git stash pop` and `git stash apply`?"
  **Answer:** "`git stash pop` applies the top stash and immediately drops it from the stash stack, whereas `git stash apply` leaves it in the stack."

## Self-check rubric

Use stash for temporary local changes, cherry-pick for one selected commit and fork for an independent repository. State how conflicts and upstream synchronization are handled.

## References and reviewed-on date

- [Git stash documentation](https://git-scm.com/docs/git-stash) — local stash behavior.
- [Android app publishing](https://developer.android.com/studio/publish) — release branch context.

Technically reviewed against primary documentation on 2026-10-13.
