---
id: "CIC-04"
question: "Compare Git merge, rebase, squash, revert, and reset."
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "A"
phase: 4
priority: "P2"
order: 423
editorial_status: "reviewed"
---

# CIC-04

## Original interview question

Compare Git merge, rebase, squash, revert, and reset.

## What the interviewer evaluates

- History effects of merge, rebase, squash, revert and reset.
- Shared versus private branch safety.

## Concept and technical explanation

Git operations govern how commit histories are joined, reshaped, or reversed across collaboration workflows:
- Comparative Behavioral Analysis:
  1. git merge:
     - Joins diverged branch histories by creating a 3-way merge commit with two parents.
     - Preserves full chronological accuracy and branch topology, but creates non-linear graph complexity with merge commit noise.
  2. git rebase:
     - Replays commits from the current branch onto the tip of the target base branch one by one.
     - Produces a pristine linear history. Rewrites commit SHA hashes; strictly prohibited on public shared branches.
  3. git squash:
     - Condenses multiple incremental commits into a single atomic commit.
     - Standard in pull request workflows (Squash and Merge) to hide intermediate exploratory commits and keep mainline history bisect-friendly.
  4. git revert:
     - Undoes a previous commit by generating a new forward commit containing the inverse diff.
     - 100% safe on shared branches because it preserves history immutability without requiring force-pushing.
  5. git reset:
     - Moves the current branch HEAD ref backward in time to a previous commit.
     - Modifies history and discards or unstages commits; destructive if pushed to remotes requiring forced updates.

## Practical walkthrough (English)

Practical Git CLI workflows comparing rebase, squash, revert, and reset:
```bash
# 1. Linear history: Rebase feature branch on updated main before PR creation:
git checkout feature/checkout-flow
git fetch origin
git rebase origin/main

# 2. Squash multiple commits interactively:
git rebase -i HEAD~3
# Mark commits as 'squash' (or 's') to collapse them into an atomic commit

# 3. Safe undo on shared main branch using revert (creates a new inverse commit):
git checkout main
git pull origin main
git revert 4f8a91b -m 1 # Use -m 1 if reverting a merge commit
git push origin main    # Safe standard push without --force

# 4. Local cleanup using reset:
git reset --soft HEAD~1 # Undoes last commit, keeping all changes staged
```

## Explanation in Arabic

قارن بين أوامر Git الأساسية: `merge`، و `rebase`، و `squash`، و `revert`، و `reset` من حيث السلوك وتعديل التاريخ وحالات الاستخدام؟

1. المقارنة الهندسية الشاملة:
   - **`git merge`**: يدمج فرعين عبر إنشاء commit جديد يُسمى Merge Commit (يمتلك 2 parents). يحافظ على التاريخ كاملاً بكل تفاصيله وتسلسله الزمني، ولكنه ينتج تاريخاً متشابكاً (Non-linear history).
   - **`git rebase`**: يعيد تشغيل (Replay) التغييرات الخاصة بالفرع الحالي فوق قمة الفرع المستهدف (HEAD). يُنشئ تاريخاً خطياً نظيفاً جداً (Linear history)، ولكنه **يعيد كتابة التاريخ (Rewrites commit hashes)**، لذا يُحظر استخدامه على الفروع العامة المشتركة.
   - **`git squash`**: يدمج عدة commits صغيرة أو تجريبية من فرع الميزة في commit واحد نظيف وذري (Atomic Commit). ممتاز لإخفاء رسائل الـ commits الفوضوية (مثل: "fix typo", "wip") قبل الدمج في Main.
   - **`git revert`**: يلغي تأثير commit قديم عبر **إنشاء commit جديد معاكس (Forward-looking inverse commit)**. آمن 100% على الفروع المشتركة لأنه لا يعبث بالتاريخ إطلاقاً.
   - **`git reset`**: يرجع مؤشر الفرع إلى نقطة زمنية سابقة في التاريخ. يمسح الـ commits من التاريخ، وإذا رُفعت للـ remote تتطلب `git push --force`، مما يجعله خطيراً على الفروع المشتركة.

## Practical walkthrough

أمثلة عملية توضح الفوارق بين هذه الأوامر في بيئة العمل اليومية:
```bash
# 1. Rebase فرعك المحلي على أحدث تغييرات main قبل فتح الـ PR (تاريخ خطي نظيف):
git checkout feature/user-profile
git fetch origin
git rebase origin/main

# 2. Squash دمج عدة commits أثناء الـ rebase التفاعلي:
git rebase -i HEAD~3
# في المحرر: غير 'pick' إلى 'squash' أو 's' للكوميتات الثانية والثالثة

# 3. Revert آمن لكوميت سبب كراش على main المشترك (ينشئ كوميت جديد يعكس التغيير):
git checkout main
git revert 4f8a91b
git push origin main # مسموح بدون force push لأن التاريخ لم يعد كتابته!

# 4. Reset محلي لإلغاء آخر كوميت مع الحفاظ على التغييرات في الكود للتعديل:
git reset --soft HEAD~1
```

## Why it matters and how it works

Git commits are immutable objects linked by parents. Rebase and reset create/move references and can require force-push on shared history. Revert applies inverse changes as a new commit; it may conflict if later changes depend on the old code.

## Worked example

Feature branch behind main: rebase locally before review if branch ownership permits; merge or squash per repository policy. If a bad commit is already on main, use revert and run tests rather than reset --hard plus force-push.

## Trade-offs and decision criteria

Merge preserves detailed history but can be noisy. Squash yields concise history but loses intermediate commit boundaries. Rebase makes linear history at cost of rewritten commit IDs. Choose based on collaboration and audit needs.

## Failure modes

A developer resets shared main and force-pushes; teammates’ branches and CI references diverge. A revert of an older commit can also conflict because code changed later; resolve and test the resulting tree.

## Production perspective

Branch protection blocks force-pushes to main, requires reviewed PRs and records release commits. Hotfix policy specifies revert versus fix-forward based on deployed impact.

## Interview answer — short

Merge joins branches preserving full history with a merge commit. Rebase replays commits linearly on top of upstream, rewriting hashes. Squash collapses multiple commits into a single atomic commit. Revert creates a new inverse commit to safely undo changes on shared branches without rewriting history, and Reset moves the branch pointer backward, altering history.

## Interview answer — structured

These five Git operations govern how branch histories are combined, rewritten, or reversed across engineering workflows.
Git merge integrates diverged branches by creating a 3-way merge commit with two parents. It guarantees complete historical accuracy and context, but creates a non-linear graph with merge commit clutter.
Git rebase replays local commits one by one on top of the target base branch, yielding a clean, linear commit history. Because it assigns new commit SHA hashes, it must never be run on public shared branches.
Git squash compresses a series of incremental commits into a single commit. It is standard in pull request merges to condense exploratory development into a single logical, bisect-friendly commit on main.
Git revert safely rolls back changes by creating a new forward commit containing the inverse diff. It preserves history immutability and causes no merge conflicts for teammates on shared branches.
Git reset adjusts the current branch HEAD backward in time. It rewrites branch history and requires forced pushes if already pushed to remotes, making it suitable strictly for local unshared work.

## Interview answer — deep senior

In team Git architecture and continuous integration governance, choosing between merge, rebase, and squash impacts debugging, git bisect operations, and release auditability.
A linear commit history generated by git rebase or squash-and-merge makes automated regression hunting with git bisect remarkably fast and reliable. When messy merge commit graphs exist, automated bisect scripts frequently stumble into broken intermediary states where commits were merged half-baked. Squash-and-merge is preferred in many mobile teams because it reduces pull request clutter to a single cohesive feature commit linked to an issue tracker identifier. However, if a large pull request contains distinct architectural refactors, squashing them destroys the context of each separate change; an interactive rebase preserving several clean, atomic commits is superior in complex architectural migrations.
The golden rule of Git rebase is never rebasing a branch that has been published and shared with other engineers. Rebase rewrites commit SHA hashes. When collaborators pull a rebased branch, Git interprets their identical local commits as divergent, creating duplicate commits and painful merge conflicts.
Finally, when production incidents require rolling back defective merges, git revert is the mandatory tool. Reverting a merge commit with git revert -m 1 creates an inverse commit advancing history forward, allowing standard pushing without dangerous force-pushing. Teams configure branch protection rules in GitHub or GitLab that strictly disallow force pushes on trunk, enforcing non-destructive reverts by operational policy.

## How to answer in the interview

- **Why:** history operations affect collaborators.
- **How:** choose merge/rebase/squash/revert/reset by shared-state boundary.
- **Trade-off:** linear history versus preserved branch context.
- **Failure case:** force reset loses public release history.
- **Production solution:** use additive revert or hotfix commits on protected branches.

## Deep-dive talking points

Prompt for commit graph, public history, revert conflict and deployment traceability.

## Follow-up questions

- **Interviewer:** "What is the primary risk of using rebase on a shared team branch?"
  **Answer:** "It rewrites commit hashes, causing teammates' local branches to diverge and creating duplicate commits and messy conflict resolutions."

- **Interviewer:** "How does squash-merge benefit git bisect?"
  **Answer:** "It ensures every commit on main is a complete, working, compilable state rather than a half-broken 'work in progress' commit."

## Self-check rubric

Show the commit-graph effect of merge, rebase and squash; use revert for a shared published change and reset for private history; describe one conflict or audit implication.

## References and reviewed-on date

- [Git reset documentation](https://git-scm.com/docs/git-reset) — reset modes.
- [Android app publishing](https://developer.android.com/studio/publish) — release traceability context.

Technically reviewed against primary documentation on 2026-10-13.
