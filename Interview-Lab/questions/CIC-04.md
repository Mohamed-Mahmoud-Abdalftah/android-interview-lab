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

“I choose Git operation based on whether commits are published. A private feature branch can be rebased for clean review; merge preserves branch structure; squash makes one integration commit. Revert is the audit-friendly way to undo an already shared change because it adds a new commit. Reset changes the branch pointer and can discard local work, so I do not use it to rewrite protected main. The mechanics matter. Git commits are immutable objects linked by parents. Rebase and reset create/move references and can require force-push on shared history. Revert applies inverse changes as a new commit; it may conflict if later changes depend on the old code. The choice has a trade-off. Merge preserves detailed history but can be noisy. Squash yields concise history but loses intermediate commit boundaries. Rebase makes linear history at cost of rewritten commit IDs. Choose based on collaboration and audit needs.”

## Interview answer — deep senior

“I reason from the commit graph and release state. Rebase changes commit identities, which is safe only when collaborators know the branch will be rewritten. A merge retains both parent histories, while squash trades granularity for simpler main. Reverting an old change is not guaranteed to apply cleanly: later commits may depend on it, so I resolve conflicts and run affected tests. Reset is useful for local cleanup, but force-resetting a shared release branch breaks traceability and may leave deployed artifacts without a clear source history. Consider a concrete case. Feature branch behind main: rebase locally before review if branch ownership permits; merge or squash per repository policy. If a bad commit is already on main, use revert and run tests rather than reset --hard plus force-push. A failure case illustrates the risk. A developer resets shared main and force-pushes; teammates’ branches and CI references diverge. A revert of an older commit can also conflict because code changed later; resolve and test the resulting tree. In production, the response is concrete. Branch protection blocks force-pushes to main, requires reviewed PRs and records release commits. Hotfix policy specifies revert versus fix-forward based on deployed impact. The decision has a trade-off. Merge preserves detailed history but can be noisy. Squash yields concise history but loses intermediate commit boundaries. Rebase makes linear history at cost of rewritten commit IDs. Choose based on collaboration and audit needs.”

## Deep-dive talking points

Prompt for commit graph, public history, revert conflict and deployment traceability.

## Follow-up questions

- [CIC-05](../cic-05/): How do reset modes differ? **Answer:** index and working-tree effects.
- [CIC-06](../cic-06/): Why revert main? **Answer:** it preserves an auditable shared history.

## Self-check rubric

Can you explain this decision, apply the example, name a trade-off and failure, and answer both follow-ups without relying on a memorized slogan?

## References and reviewed-on date

- [Git reset documentation](https://git-scm.com/docs/git-reset) — reset modes.
- [Android app publishing](https://developer.android.com/studio/publish) — release traceability context.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
