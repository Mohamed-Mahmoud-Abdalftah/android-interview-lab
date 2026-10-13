---
id: "CIC-15"
question: "What Git conflicts can a revert of an older commit cause?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "B"
phase: 4
priority: "P2"
order: 434
editorial_status: "reviewed"
---

# CIC-15

## Original interview question

What Git conflicts can a revert of an older commit cause?

## What the interviewer evaluates

- Textual and semantic conflicts when reverting an old commit.
- Merge revert and deployed-state risks.

## Explanation in Arabic

`git revert` لcommit قديم بيحاول يعكس patch على code الحالي. لو commits بعده عدّلت نفس السطور ممكن conflict نصي؛ ولو اعتمدت على behavior القديم ممكن revert ينجح Git لكن يكسر build أو runtime. Revert merge commit يحتاج mainline parent. ولا تنسى migration اتطبقت بالفعل على devices؛ عكس code لا يعكس data.

### Practical walkthrough in Egyptian Arabic

Revert لcommit قديم ممكن يتصادم مع commits لاحقة نقلت الملف، غيرت API، أو بنت على schema/behavior الذي ستزيله. Git قد يعطي conflict نصي واضح، لكن الأخطر semantic conflict: revert ينجح ويكسر feature تعتمد على التغيير. راجع commits بعد الهدف، اعمل revert في branch، افحص diff، compile للvariants المعنية، وشغّل regression tests. لو كان merge commit، حدد mainline parent عن فهم بدل تجربة أمر عشوائي.

## Why it matters and how it works

Git merges inverse changes into present tree, not the historical tree at the old commit. Conflict resolution needs understanding of later edits and dependencies. Tests of current combined state are necessary even if revert applies cleanly.

## Worked example

Commit A adds payment status `UNKNOWN`; B later adds UI handling. Reverting A alone may compile-fail or silently map unknown to declined. Review dependency graph, revert B too or fix-forward state machine, then test payment timeout and recovery.

## Trade-offs and decision criteria

Reverting is collaboration-safe for shared history, but can require a series of coordinated commits. Reset avoids patch conflicts only by rewriting history, which is unsafe for shared release branch and does not undo deployed side effects.

## Failure modes

Auto-resolving conflict with “ours” may leave half-reverted logic. Review tests and schema migrations, check backend compatibility and release artifact behavior.

## Production perspective

Hotfix PR includes conflict rationale, affected tests, data migration plan and rollout monitoring. Preserve source-to-artifact traceability.

## Interview answer — short

“An old revert can conflict where later commits changed the patch, or apply cleanly yet break code that depends on it. I inspect dependencies, resolve deliberately and test deployed-state compatibility.”

## Interview answer — structured

“Revert creates an inverse commit against today’s tree. Later edits to the same lines cause merge conflicts; later semantic dependencies can cause hidden bugs. I inspect commits after the target, resolve code intentionally, and run affected tests. For merge commits I choose the correct mainline. I also assess data migrations and backend changes because a source revert cannot undo effects already deployed.”

## Interview answer — deep senior

“An old commit does not exist in isolation anymore. Later commits may rename its files, call APIs it introduced, change database schema, or make the original behavior a prerequisite. A revert may produce textual conflicts, or it may apply cleanly while creating a semantic regression. I inspect the commit graph and dependencies, create a rollback branch from the current release head, perform the revert there and review the resulting diff. Then I compile the affected variants and run the journeys that consumed the changed contract, including migration and data compatibility where relevant. Reverting a merge requires an explicit mainline choice and has consequences for later merges, so I treat that as a planned operation. For a production incident I may prefer a small compensating fix if it preserves newer dependent work more safely than a broad revert. The aim is a tested current-state change with auditable history, not just a Git command that exits zero.”

## How to answer in the interview

- **Why:** later commits can depend on older behavior.
- **How:** inspect graph, revert on branch, review current diff.
- **Trade-off:** broad revert versus narrow compensating fix.
- **Failure case:** clean apply creates semantic breakage.
- **Production solution:** test affected variants and migrations.

## Deep-dive talking points

Prompt for inverse patch, textual versus semantic conflicts, merge mainline and shipped migration.

## Follow-up questions

- [CIC-06](../cic-06/): Why revert shared history? **Answer:** preserve public commit identities.
- [CIC-17](../cic-17/): What about hotfix branches? **Answer:** start from deployed base and propagate deliberately.

## Self-check rubric

Draw how a later commit can depend on lines changed by an older commit; predict the revert conflict, resolve the intended behavior and run targeted tests rather than assuming inverse patches commute.

## References and reviewed-on date

- [Git revert documentation](https://git-scm.com/docs/git-revert) — revert semantics.
- [Room migration guide](https://developer.android.com/training/data-storage/room/migrating-db-versions) — deployed schema effects.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
