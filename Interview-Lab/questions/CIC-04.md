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

Merge joins branches preserving full history with a merge commit. Rebase replays commits linearly on top of upstream, rewriting hashes. Squash collapses multiple commits into a single atomic commit. Revert creates a new inverse commit to safely undo changes on shared branches, and Reset moves the branch pointer backward, rewriting history.

## Interview answer — structured

These five Git operations govern how branch histories are combined, rewritten, or corrected.

First, **`git merge`**. Next, integrates diverged branches by creating a 3-way merge commit with two parents. It guarantees complete historical accuracy and context, but creates a non-linear graph with merge commit noise.
**`git rebase`**. Re-applies local commits one by one on top of the target base branch. Yields a clean, perfectly linear commit history. Because it assigns new commit SHA hashes, it must never be run on public shared branches.
**`git squash`**. Compresses a series of incremental commits into a single commit. Frequently used in PR merges (Squash and Merge) to condense exploratory development into a single logical, bisect-friendly commit on main.
**`git revert`**. Safely rolls back changes by creating a new forward commit containing the inverse diff. It preserves history and causes no merge conflicts for teammates on shared branches.
**`git reset`**. Finally, adjusts the current branch HEAD backward in time. Rewrites branch history and requires forced pushes if already remote, making it suitable only for local unshared work.


## Interview answer — deep senior

In team Git architecture and CI governance, choosing between merge, rebase, and squash impacts debugging and bisecting.

First, a Git Bisect Optimization is a linear history generated by `git rebase` or `squash and merge` makes `git bisect` fast and reliable. When messy merge commit graphs exist, automated bisect scripts frequently stumble into broken intermediary states where commits were merged half-baked. Next, with The Squash vs. Rebase Debate in PRs, squash-and-merge is preferred in many Android teams because it reduces PR clutter to a single cohesive feature commit linked to a Jira/Issue ID. However, if a 2,000-line PR contains 10 logical architectural refactors, squashing them destroys the context of each distinct change. A clean interactive rebase (`git rebase -i`) preserving 3 atomic commits is superior in complex refactorings.
Finally, with Golden Rule of Git Rebase, never rebase a branch that has been published and shared with other engineers. Rebase changes commit SHAs; when peers pull the rebased branch, Git interprets their identical local commits as divergent, creating duplicate commits and painful merge conflicts.


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
