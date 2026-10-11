---
id: "CIC-19"
question: "The app release pipeline deploys the wrong flavor. How do you prevent recurrence?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "C"
phase: 4
priority: "P2"
order: 438
editorial_status: "reviewed"
---

# CIC-19

## Original interview question

The app release pipeline deploys the wrong flavor. How do you prevent recurrence?

## What the interviewer evaluates

- Wrong-flavor root cause and preventative artifact assertions.
- User impact containment and process repair.

## Explanation in Arabic

لو pipeline نشر wrong flavor، أولًا نوقف rollout ونفهم هل التطبيق اتصل بbackend غلط أو حمل keys/permissions غير مناسبة. بعدين نفحص variant task، artifact metadata، applicationId، signing cert، host وPlay track. الإصلاح مش تغيير اسم job فقط؛ CI لازم تعمل assertion على الـbuilt AAB قبل upload، وتربط target environment بmetadata موثوقة.

## Why it matters and how it works

Gradle variant name, source sets and manifest merging determine packaged config. The publish task can be parameterized incorrectly or consume a stale artifact. A pre-upload gate checks the actual output and expected tuple; branch name is not reliable proof of flavor.

## Worked example

CI expected tuple: `prodRelease`, package `com.example.pay`, production host, release certificate and production Play app. If any mismatch, stop. For an incident, halt rollout, disable risky backend behavior, assess installed cohort and ship a corrected version.

## Trade-offs and decision criteria

Additional assertions slow release slightly but catch high-impact mistakes. Separate Play apps/accounts and backend rejection of test credentials provide defense in depth. Remote config is not a substitute for verified artifact identity.

## Failure modes

Pipeline uploads `stagingRelease` because wildcard selects newest AAB. Tests passed on `prodRelease`, so evidence mismatches shipped artifact. Pin exact path and compare SHA tested versus uploaded.

## Production perspective

Postmortem records root cause, affected installs, data exposure assessment and gate improvements. Release dashboard displays variant tuple before approval.

## Interview answer — short

“I halt rollout, assess installed impact, then add a pre-upload assertion on the actual AAB’s package, host, signing, variant and target track. Tests must cover the artifact that ships.”

## Interview answer — structured

“Wrong-flavor publishing is an artifact-selection and environment-boundary failure. I stop new distribution, assess whether users reached the wrong backend, and inspect the tested versus uploaded hashes. The pipeline then binds one explicit Gradle task to one output path, verifies applicationId, endpoint, signing identity and Play app/track, and rejects any mismatch. Separate backend/provider accounts and staged rollout limit damage. The mechanics matter. Gradle variant name, source sets and manifest merging determine packaged config. The publish task can be parameterized incorrectly or consume a stale artifact. A pre-upload gate checks the actual output and expected tuple; branch name is not reliable proof of flavor. The choice has a trade-off. Additional assertions slow release slightly but catch high-impact mistakes. Separate Play apps/accounts and backend rejection of test credentials provide defense in depth. Remote config is not a substitute for verified artifact identity.”

## Interview answer — deep senior

“I do not stop at changing the variable that caused this incident. I map the full source-to-release chain: variant matrix, merged manifest, AAB hash, signing identity, upload task and Play target. A test that checks only a build variable can pass while stale output is uploaded, so I inspect the artifact itself and enforce an expected tuple. I add a canary release test that deliberately swaps flavors and must fail. For already installed wrong builds, I use backend controls and a corrected compatible release; Play rollout halt does not uninstall them. Consider a concrete case. CI expected tuple: `prodRelease`, package `com.example.pay`, production host, release certificate and production Play app. If any mismatch, stop. For an incident, halt rollout, disable risky backend behavior, assess installed cohort and ship a corrected version. A failure case illustrates the risk. Pipeline uploads `stagingRelease` because wildcard selects newest AAB. Tests passed on `prodRelease`, so evidence mismatches shipped artifact. Pin exact path and compare SHA tested versus uploaded. In production, the response is concrete. Postmortem records root cause, affected installs, data exposure assessment and gate improvements. Release dashboard displays variant tuple before approval. The decision has a trade-off. Additional assertions slow release slightly but catch high-impact mistakes. Separate Play apps/accounts and backend rejection of test credentials provide defense in depth. Remote config is not a substitute for verified artifact identity.”

## Deep-dive talking points

Prompt for tested/uploaded hash, actual AAB inspection, endpoint tuple, already-installed impact.

## Follow-up questions

- [CIC-16](../cic-16/): What are flavor dimensions? **Answer:** environment variants with explicit application/host identity.
- [CIC-14](../cic-14/): Does halt undo install? **Answer:** no; plan mitigation for installed cohort.

## Self-check rubric

Can you explain the mechanism, apply the example, justify a trade-off, identify a failure mode, and answer both follow-ups?

## References and reviewed-on date

- [Android build variants](https://developer.android.com/build/build-variants) — variant configuration.
- [Android App Bundle](https://developer.android.com/guide/app-bundle) — packaged artifact.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
