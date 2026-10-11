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

“On main, other developers and CI have already referenced the published commits. Reset plus force-push would rewrite that history. Revert produces an auditable new commit and normal PR/release flow. However, later code may depend on the reverted change, so I resolve conflicts and run tests. For a shipped migration or backend contract, I also assess compatibility and may need a forward repair. The mechanics matter. A revert applies inverse patch against current tree, so it may conflict or produce semantic problems when subsequent commits changed the same code. Git history remains append-only, preserving CI and release references. A revert of a merge requires choosing a mainline parent. The choice has a trade-off. Revert is safer for collaboration but can require repair and a new release; reset is suitable for disposable local branch cleanup. A backend feature flag may reduce live risk faster while the revert builds.”

## Interview answer — deep senior

“I separate source rollback from operational rollback. Git revert can restore code behavior in a new artifact, but it cannot uninstall an AAB, recover data deleted by a migration or erase a server-side side effect. I inspect dependent commits and schemas, create a targeted revert or fix-forward, test the current tree, and stage rollout. For an urgent active incident, a server feature gate may reduce exposure while the app release propagates. Reset remains appropriate for private local history, not shared release provenance. Consider a concrete case. A bad payment validation commit is on main and included in internal build. Create a revert PR, resolve a conflict with a later UI change, run payment tests and release a new artifact. Do not reset main to yesterday because another team already based work on it. A failure case illustrates the risk. Reverting a database migration source does not reverse schemas already applied on user devices. Plan compatible forward migration or fix-forward. Verify the deployed state, not just Git diff. In production, the response is concrete. Incident runbook records commit, revert SHA, artifact version, schema compatibility and rollout status. Branch protection prevents force-push to release branches. The decision has a trade-off. Revert is safer for collaboration but can require repair and a new release; reset is suitable for disposable local branch cleanup. A backend feature flag may reduce live risk faster while the revert builds.”

## Deep-dive talking points

Prompt for public commit references, inverse patch conflict, released migration, feature gate.

## Follow-up questions

- [CIC-15](../cic-15/): Why might old revert conflict? **Answer:** later commits changed same lines or depend semantically.
- [CIC-14](../cic-14/): Can halt rollout remove installs? **Answer:** no; plan fix-forward compatibility.

## Self-check rubric

Can you explain this decision, apply the example, name a trade-off and failure, and answer both follow-ups without relying on a memorized slogan?

## References and reviewed-on date

- [Git revert documentation](https://git-scm.com/docs/git-revert) — inverse commit semantics.
- [Android Room migrations](https://developer.android.com/training/data-storage/room/migrating-db-versions) — shipped schema considerations.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
