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

### Practical walkthrough in Egyptian Arabic

لو AAB اتوقّع بمفتاح غلط، أوقف promotion واعرف هل upload اترفض أم وصل track وأي مستخدم استلمه. فرّق بين upload key وapp signing key في Play App Signing؛ إجراءات الاسترداد مختلفة ولا ينفع تفترض استبدال مفتاح تطبيق منشور ببساطة. راجع CI secret reference وfingerprint قبل الرفع، اعزل credential الخطأ، ثم ابنِ artifact صحيح بهوية source/version مناسبة حسب حالة الرفع. لازم incident log يحفظ ماذا نُشر فعلًا.

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

“Wrong-flavor publishing is an artifact-selection and environment-boundary failure. I stop new distribution, assess whether users reached the wrong backend, and inspect the tested versus uploaded hashes. The pipeline then binds one explicit Gradle task to one output path, verifies applicationId, endpoint, signing identity and Play app/track, and rejects any mismatch. Separate backend/provider accounts and staged rollout limit damage.”

## Interview answer — deep senior

“First I contain the release: stop promotion and establish whether the bundle was rejected, accepted only into an internal track, or reached users. I compare the uploaded certificate fingerprint with the expected upload identity and distinguish it from the app-signing key managed by Play App Signing. Those keys have different roles and recovery procedures, so I follow the store’s current documented flow rather than assuming I can replace a production signing key at will. I inspect the trusted CI job, secret reference and artifact provenance, revoke or rotate a compromised credential if needed, and rebuild from the intended protected commit. I validate package ID, version code and signing fingerprint before another upload, then test install/update on the relevant track. A wrong key may be a configuration mistake or an intrusion signal, so audit logs and access review matter. I preserve evidence of which artifact, if any, users received and communicate a correction plan based on that fact.”

## How to answer in the interview

- **Why:** signing identity controls update trust.
- **How:** contain upload and compare certificate fingerprints.
- **Trade-off:** speed versus careful key recovery.
- **Failure case:** assuming upload and app-signing keys are identical.
- **Production solution:** verify trusted release job and store state.

## Deep-dive talking points

Prompt for tested/uploaded hash, actual AAB inspection, endpoint tuple, already-installed impact.

## Follow-up questions

- [CIC-16](../cic-16/): What are flavor dimensions? **Answer:** environment variants with explicit application/host identity.
- [CIC-14](../cic-14/): Does halt undo install? **Answer:** no; plan mitigation for installed cohort.

## Self-check rubric

Specify variant identity assertions in build metadata and pre-publish gates; demonstrate how package ID, endpoint and signing certificate would catch the wrong flavor before Play upload.

## References and reviewed-on date

- [Android build variants](https://developer.android.com/build/build-variants) — variant configuration.
- [Android App Bundle](https://developer.android.com/guide/app-bundle) — packaged artifact.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
