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

### Practical walkthrough in Egyptian Arabic

Production hotfix يبدأ من tag أو commit النسخة المنشورة، مش من feature branch متباعد. اعزل أقل تعديل يصلح incident، اختبر release variant والمسار المتأثر، ثم انشر versionCode أعلى تدريجيًا. بعدين انقل الإصلاح لـmain وبقية release branches بـmerge أو cherry-pick مع فحص conflicts semantic. لو main فيها refactor يجعل نفس patch غير صحيح، اكتب equivalent fix واختبره. احتفظ بالحادثة والـartifact والcommit المرتبطين.

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

“I branch the hotfix from the code that actually shipped, identified by the production tag and artifact provenance, rather than from a moving main branch full of unrelated features. I make the smallest safe change, add a regression test for the incident, build the production release variant and publish a higher-version candidate through the urgent release gate. Then I forward-port the fix to main and supported branches with merge or cherry-pick as appropriate, reviewing semantic differences caused by divergence. A patch that applies cleanly to refactored main may still behave differently, so each destination gets its own tests. I avoid rewriting public history or merging unfinished features into the emergency release. If the issue can be contained by a safe server control, I may reduce exposure while the binary is prepared. The trade-off is some duplicated integration work for isolation and speed. I track which users received which build and ensure the fix does not abandon in-flight financial or data operations.”

## How to answer in the interview

- **Why:** hotfix must match shipped code.
- **How:** branch from production tag and forward-port fix.
- **Trade-off:** isolation speed versus duplicate integration.
- **Failure case:** patch applies but behavior differs on main.
- **Production solution:** test release variant and every destination branch.

## Deep-dive talking points

Prompt for deployed artifact base, minimal scope, branch propagation, compatibility and staged rollout.

## Follow-up questions

- [CIC-07](../cic-07/): When cherry-pick? **Answer:** surgical propagation with dependency review.
- [CIC-14](../cic-14/): How ship hotfix safely? **Answer:** stage and monitor installed-version effects.

## Self-check rubric

Branch the hotfix from the production tag, cherry-pick only the fix, test and release a higher version, then merge or cherry-pick the fix forward into diverged branches.

## References and reviewed-on date

- [Git cherry-pick documentation](https://git-scm.com/docs/git-cherry-pick) — patch replay.
- [Android publishing](https://developer.android.com/studio/publish) — release process.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
