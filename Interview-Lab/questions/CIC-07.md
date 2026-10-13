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

`stash` يخزن working-tree/index changes مؤقتًا بعيد عن commit الحالي؛ `cherry-pick` ينسخ أثر commit محدد لفرع آخر بcommit جديد؛ `fork` نسخة repository تحت حساب آخر غالبًا لcontribution. دول بيحلوا مشاكل مختلفة: تنضيف workspace مؤقت، نقل hotfix، أو فصل صلاحيات التعاون.

### Practical walkthrough in Egyptian Arabic

`stash` رف مؤقت لتغييرات غير جاهزة، لكنه مش backup دائم؛ سميه وراجع محتواه قبل `apply`/`pop`. `cherry-pick` ينسخ أثر commit محدد لفرع تاني بهوية commit جديدة، مفيد hotfix بين release وmain مع مراجعة conflicts. `fork` نسخة repository تحت حساب/مساحة منفصلة لساهم خارجي، وتحتاج sync مع upstream. مثال: لا تعمل cherry-pick لسطر security fix وتنسى test أو migration الذي جاء في commit آخر.

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

“Stash parks local edits; cherry-pick replays a commit onto another branch; fork creates a separate repository for collaboration. I review conflicts and dependencies, especially for hotfix picks.”

## Interview answer — structured

“I use stash for short-lived uncommitted work when switching tasks, cherry-pick for a specific reviewed fix that must enter another branch, and fork when contributors should work without direct repository write access. Cherry-pick creates a new hash and may need dependent commits; stash can conflict on reapply. I prefer a branch for long-lived work and record hotfix provenance.”

## Interview answer — deep senior

“These tools solve different collaboration problems. Stash shelves a local worktree/index state so I can switch context, but it is not a durable review or release artifact; I name it and inspect what was captured. Cherry-pick applies the changes from a specific commit to another branch, creating a new commit identity. It is useful for a narrow hotfix across supported release branches, but I review dependencies, conflicts and tests in the destination context rather than assuming the copied patch has the same meaning. A fork is a separate repository lineage, often used for outside contributions, with an upstream remote for syncing. In an Android release I might stash unrelated local UI edits, branch from a production tag, fix a crash and cherry-pick the tested fix to main. I would not cherry-pick only the implementation and forget its migration or instrumentation test. The trade-off of selective commits is speed versus the risk of splitting one logical change.”

## How to answer in the interview

- **Why:** context switching and branch transfer have different needs.
- **How:** stash local state, cherry-pick a commit, fork a repository.
- **Trade-off:** selective patch speed versus dependency risk.
- **Failure case:** hotfix lacks its paired migration.
- **Production solution:** review destination diff and run its tests.

## Deep-dive talking points

Prompt for local versus repo scope, new commit SHA, dependent commits, fork PR secret boundary.

## Follow-up questions

- [CIC-17](../cic-17/): How move urgent hotfix? **Answer:** fix on release base and propagate tested commit carefully.
- [CIC-18](../cic-18/): Are fork PRs trusted? **Answer:** no; keep secrets out of their jobs.

## Self-check rubric

Use stash for temporary local changes, cherry-pick for one selected commit and fork for an independent repository. State how conflicts and upstream synchronization are handled.

## References and reviewed-on date

- [Git stash documentation](https://git-scm.com/docs/git-stash) — local stash behavior.
- [Android app publishing](https://developer.android.com/studio/publish) — release branch context.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
