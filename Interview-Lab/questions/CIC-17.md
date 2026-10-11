---
id: "CIC-17"
question: "A production hotfix is needed while feature branches have diverged. Explain your Git strategy."
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "C"
phase: 4
priority: "P2"
order: 436
editorial_status: "reviewed"
---

# CIC-17

## Original interview question

A production hotfix is needed while feature branches have diverged. Explain your Git strategy.

## What the interviewer evaluates

- Hotfix from deployed base with branch divergence.
- Propagation, compatibility and release provenance.

## Explanation in Arabic

لو production محتاج hotfix وfeature branches اختلفت، أبدأ من tag/commit اللي اتشحن فعلًا، أعمل minimal fix مع test، وأطلع release candidate منفصل. بعدها أنقل نفس المنطق لـmain/feature branches بـmerge أو cherry-pick مدروس، وأتحقق من conflicts. ما أدمجش features غير جاهزة في hotfix. لو schema/backend اتغيروا لازم نفحص compatibility مع النسخ المثبتة.

## Why it matters and how it works

Hotfix source should match deployed artifact provenance, including mapping and dependencies. Cherry-picking replays a patch with new hash and may need dependent changes. Release branch and main each need tests in their own context.

## Worked example

Production `2.3.1` has token crash; main contains unfinished checkout refactor. Branch from `v2.3.1`, fix token handling, run release tests, ship `2.3.2` staged. Then apply equivalent change to main, possibly with a different implementation due to refactor.

## Trade-offs and decision criteria

Minimal patch lowers regression risk but may leave technical debt for main. Fix-forward on main could be faster if divergence is small and safe; choose based on deployed risk and test evidence.

## Failure modes

Blind cherry-pick compiles on release branch but breaks new main architecture. Review semantics and run both test suites. Never reset shared main or tag a build from an unknown dirty tree.

## Production perspective

Incident log maps deployed version, hotfix SHA, main follow-up and rollout state. Feature gates can contain impact while Play propagation occurs.

## Interview answer — short

“I branch from the deployed tag for a minimal, tested hotfix, release it separately, then propagate the logical fix to divergent branches and verify each context.”

## Interview answer — structured

“I identify the exact production commit and artifact, create a hotfix branch from that base, implement a narrow fix and run the release-risk tests. I ship a new version with staged monitoring rather than pulling unfinished feature work into production. Then I merge or cherry-pick the fix to main, resolving semantic differences caused by divergence. Schema and backend compatibility with installed clients are part of the decision. ”

## Interview answer — deep senior

“I first contain customer impact with a server flag if possible, then verify the deployed tag, AAB hash and mapping. The hotfix branch changes only what is needed and retains compatibility with current server and local data. I test the exact minified flavor, stage rollout, and maintain recovery for already affected users. I propagate the fix to main and active release branches, recording different SHAs if cherry-picked. Conflict-free application is not enough; each branch has its own architecture and tests.”

## Deep-dive talking points

Prompt for deployed artifact base, minimal scope, branch propagation, compatibility and staged rollout.

## Follow-up questions

- [CIC-07](../cic-07/): When cherry-pick? **Answer:** surgical propagation with dependency review.
- [CIC-14](../cic-14/): How ship hotfix safely? **Answer:** stage and monitor installed-version effects.

## Self-check rubric

Can you explain the mechanism, apply the example, justify a trade-off, identify a failure mode, and answer both follow-ups?

## References and reviewed-on date

- [Git cherry-pick documentation](https://git-scm.com/docs/git-cherry-pick) — patch replay.
- [Android publishing](https://developer.android.com/studio/publish) — release process.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
