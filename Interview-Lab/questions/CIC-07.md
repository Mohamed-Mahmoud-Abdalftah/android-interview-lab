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

Git stash shelves uncommitted changes to allow switching branches cleanly. Git cherry-pick applies a specific commit by hash from another branch onto the current branch without merging the whole branch. A Fork is a server-side repository copy allowing developers to contribute via pull requests without write permissions to the upstream repository.

## Interview answer — structured

These three Git mechanisms solve distinct workflow and isolation problems:

1. **`git stash`**:
   - Temporarily shelves uncommitted changes (both staged and unstaged) onto an internal stack (`stash@{0}`), returning the working directory to a pristine HEAD state.
   - Crucial for rapid context-switching, such as investigating an urgent production bug while mid-refactor. Using `-u` (include untracked) ensures newly created files are also stashed.

2. **`git cherry-pick <commit-sha>`**:
   - Extracts the exact diff introduced by a single commit from any branch and applies it as a brand-new commit on the currently checked-out branch.
   - Ideal for backporting critical bug fixes from `main` to existing maintenance or release branches without pulling unreleased features.

3. **Fork**:
   - A remote server-side clone of a repository hosted under an independent user or organization account.
   - Establishes a decoupled contribution boundary standard in open-source projects or enterprise contractor models, where external contributors lack direct push permissions and submit pull requests across forks.

## Interview answer — deep senior

From an engineering governance standpoint, there are subtle pitfalls with cherry-pick and stash:

1. **The Cherry-Pick Duplicate Commit Hazard**: When you cherry-pick commit `A` into branch `B`, Git creates a new commit `A'` with a different hash. If branch `B` is later merged back into the original branch, Git must reconcile two commits that share identical diffs. In complex histories, this can trigger redundant conflict resolution or misleading blame graphs. Always record origin metadata using `git cherry-pick -x` to append the source commit hash to the commit message.

2. **Stash Volatility in Team Environments**: Git stashes are local to your workstation and not backed up to the remote repository. Leaving large, multi-day refactors in `git stash` risks unrecoverable data loss during machine failures or accidental directory cleanups (`git stash drop` or hard cleans). Incomplete work should instead be committed to a personal remote draft branch (`draft/feature-wip`).

3. **Upstream Fork Synchronization**: In forked workflows, keeping the local fork synchronized with `upstream` via automated rebase workflows prevents massive drift and painful merge conflicts when PRs are opened against the canonical repo.

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
