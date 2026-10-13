---
id: "CIC-06"
question: "When is revert safer than reset on shared branches?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "A"
phase: 4
priority: "P2"
order: 425
editorial_status: "reviewed"
---

# CIC-06

## Original interview question

When is revert safer than reset on shared branches?

## What the interviewer evaluates

- Shared-history rollback and auditability.
- Limits of revert for migrations and later dependent commits.

## Explanation in Arabic

على branch مشترك أو release branch، `revert` بيضيف commit يعكس change قديم من غير ما يغير hashes اللي الناس سحبتها. `reset` ينقل branch pointer وforce-push ممكن يكسر شغل الآخرين ويضيّع provenance. لكن revert مش زر سحري: لو commits أحدث معتمدة على القديم، هتظهر conflicts أو behavior مكسور لازم يتراجع ويُختبر.

### Practical walkthrough in Egyptian Arabic

لو commit نازل على `main` وكل الفريق بنا عليه، `reset` وforce push هيغيّروا التاريخ اللي عندهم. `revert` يضيف commit جديد يلغي الأثر بدون تغيير identities القديمة. لكن revert مش زر سحري: لو فيه commits لاحقة تعتمد على API الذي أُلغي، هيظهر conflict أو build failure يحتاج تعديل. راجع diff النهائي وشغّل tests للـvariant المتأثر، وبعدها أصلح forward branches أو release branches حسب السياسة.

## Why it matters and how it works

A revert applies inverse patch against current tree, so it may conflict or produce semantic problems when subsequent commits changed the same code. Git history remains append-only, preserving CI and release references. A revert of a merge requires choosing a mainline parent.

## Worked example

A bad payment validation commit is on main and included in internal build. Create a revert PR, resolve a conflict with a later UI change, run payment tests and release a new artifact. Do not reset main to yesterday because another team already based work on it.

## Trade-offs and decision criteria

Revert is safer for collaboration but can require repair and a new release; reset is suitable for disposable local branch cleanup. A backend feature flag may reduce live risk faster while the revert builds.

## Failure modes

Reverting a database migration source does not reverse schemas already applied on user devices. Plan compatible forward migration or fix-forward. Verify the deployed state, not just Git diff.

## Production perspective

Incident runbook records commit, revert SHA, artifact version, schema compatibility and rollout status. Branch protection prevents force-push to release branches.

## Interview answer — short

“Revert is safer on shared branches because it preserves existing commits and adds an inverse change. I still review conflicts and deployed state; a Git revert cannot undo a database migration already run on devices.”

## Interview answer — structured

“On main, other developers and CI have already referenced the published commits. Reset plus force-push would rewrite that history. Revert produces an auditable new commit and normal PR/release flow. However, later code may depend on the reverted change, so I resolve conflicts and run tests. For a shipped migration or backend contract, I also assess compatibility and may need a forward repair.”

## Interview answer — deep senior

“Revert is safer on shared branches because it records a compensating change instead of rewriting history that other contributors and release systems already reference. If commit A introduced a bad feature and B and C landed afterward, resetting main to before A would also move away B and C or force everyone to reconcile a new history. Reverting A creates a new commit whose diff is reviewed and tested like any other change. I still inspect dependencies: later code may call APIs introduced by A, so the revert can conflict or compile yet fail a user journey. In a release incident I select the smallest rollback, run the release-like checks and preserve the artifact/commit link. If the bad change was a merge commit, I explicitly choose the mainline parent and review the resulting diff. The trade-off is an extra commit and occasional conflict resolution, but the operational history remains auditable and teammates do not have to repair their local branches.”

## How to answer in the interview

- **Why:** shared refs already depend on published commits.
- **How:** revert with a reviewed compensating commit.
- **Trade-off:** auditability versus extra history.
- **Failure case:** later commits may rely on reverted API.
- **Production solution:** run release checks on the resulting branch.

## Deep-dive talking points

Prompt for public commit references, inverse patch conflict, released migration, feature gate.

## Follow-up questions

- [CIC-15](../cic-15/): Why might old revert conflict? **Answer:** later commits changed same lines or depend semantically.
- [CIC-14](../cic-14/): Can halt rollout remove installs? **Answer:** no; plan fix-forward compatibility.

## Self-check rubric

Explain why revert adds a new inverse commit without rewriting shared history; identify a case where reverting an old commit conflicts with later changes and how you would verify the result.

## References and reviewed-on date

- [Git revert documentation](https://git-scm.com/docs/git-revert) — inverse commit semantics.
- [Android Room migrations](https://developer.android.com/training/data-storage/room/migrating-db-versions) — shipped schema considerations.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
