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

`merge` يضم تاريخ فرعين ويحتفظ بالbranch topology؛ `rebase` يعيد تشغيل commits فوق base جديد فيغيّر hashes؛ `squash` يجمع commits؛ `revert` يعمل commit عكسي؛ `reset` ينقل branch pointer وقد يمسح working changes حسب mode. على shared branch نفضل revert للتراجع عشان التاريخ ما يتكتبش من جديد.

### Practical walkthrough in Egyptian Arabic

في hotfix: `merge` يحتفظ بتاريخ الفرعين ويصنع merge commit؛ `rebase` يعيد كتابة commits فرعك فوق base أحدث؛ `squash` يجمع تغييرات قبل الدمج؛ `revert` يصنع commit عكسي يحافظ على تاريخ shared branch؛ `reset` ينقل مؤشر branch وقد يرمي تغييرات حسب mode. ما تعملش force push على branch مشترك عشان تتخلص من release سيئ. لو hotfix لازم يروح `main` وrelease branch، cherry-pick أو merge حسب السياسة مع اختبار كل نسخة.

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

“Merge combines histories, rebase rewrites a branch onto a new base, squash condenses commits, revert adds an inverse commit, and reset moves a ref. On shared branches, revert is normally safer than history rewrite.”

## Interview answer — structured

“I choose Git operation based on whether commits are published. A private feature branch can be rebased for clean review; merge preserves branch structure; squash makes one integration commit. Revert is the audit-friendly way to undo an already shared change because it adds a new commit. Reset changes the branch pointer and can discard local work, so I do not use it to rewrite protected main.”

## Interview answer — deep senior

“I choose the Git operation from the history contract. Merge joins branches without rewriting existing commits, making it appropriate when shared history matters. Rebase replays my local commits on a new base and can simplify review, but rebasing a published branch changes commit identities for collaborators. Squash creates a compact final change when the intermediate commits have no independent value. Revert adds a new commit that reverses an earlier change, which is usually the safe operation on a shared release branch; reset moves the branch pointer and is most useful for my own unpublished history. In a production hotfix I branch from the release commit, make the smallest fix, run release checks, then merge or cherry-pick it back to main and other supported branches with explicit conflict review. I avoid assuming a successful cherry-pick implies the same runtime behavior, because surrounding code may differ. The trade-off is clean history versus provenance, so I preserve an auditable link between incident, fix commit and release artifact.”

## How to answer in the interview

- **Why:** history operations affect collaborators.
- **How:** choose merge/rebase/squash/revert/reset by shared-state boundary.
- **Trade-off:** linear history versus preserved branch context.
- **Failure case:** force reset loses public release history.
- **Production solution:** use additive revert or hotfix commits on protected branches.

## Deep-dive talking points

Prompt for commit graph, public history, revert conflict and deployment traceability.

## Follow-up questions

- [CIC-05](../cic-05/): How do reset modes differ? **Answer:** index and working-tree effects.
- [CIC-06](../cic-06/): Why revert main? **Answer:** it preserves an auditable shared history.

## Self-check rubric

Show the commit-graph effect of merge, rebase and squash; use revert for a shared published change and reset for private history; describe one conflict or audit implication.

## References and reviewed-on date

- [Git reset documentation](https://git-scm.com/docs/git-reset) — reset modes.
- [Android app publishing](https://developer.android.com/studio/publish) — release traceability context.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
