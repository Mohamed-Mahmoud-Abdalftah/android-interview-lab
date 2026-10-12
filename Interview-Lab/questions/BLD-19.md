---
id: "BLD-19"
question: "A release bundle was signed with the wrong key. How do you contain it and correct the pipeline?"
topic: "Gradle, AGP, R8, Signing & Release Engineering"
code: "BLD"
group: "C"
phase: 4
priority: "P1"
order: 393
editorial_status: "reviewed"
---

# BLD-19

## Original interview question

A release bundle was signed with the wrong key. How do you contain it and correct the pipeline?

## What the interviewer evaluates

- Determine whether artifact was uploaded, accepted or distributed.
- Halt promotion, preserve evidence and distinguish key roles.
- Rebuild/re-sign safely with verification and incident review.

## Explanation in Arabic

أوقف upload/promotion فورًا واعرف الحالة: AAB محلية فقط، Play رفضها لأن upload certificate غلط، أم تم قبول/توزيع artifact في قناة معينة؟ احفظ hash/logs بدون نشر secrets. قارن certificate fingerprint مع upload key المسجل، وميّزها عن app-signing key التي يستخدمها Play للأجهزة. لو مجرد wrong upload key، أصلح protected CI secret/config وأعد build أو signing من source/toolchain موثوق مع versionCode صالح، ثم افحص fingerprint قبل الرفع واختبر internal track. لو key مشبوهة أو artifact وُزع بالفعل، اتبع incident/Play recovery والـrollout halt. لا “تصلح” signed AAB بتعديل bytes يدويًا.

## Why it matters and how it works

Play App Signing verifies uploads against the registered upload certificate and signs device APKs with the app-signing key. A wrong-key AAB may be rejected before distribution; its containment differs from a compromised signing identity or already served bad release. Release artifacts are cryptographically tied to their signatures, so a corrected pipeline should produce and verify a new immutable artifact.

## Worked example

CI's `prodRelease` task accidentally reads a staging upload keystore. A pre-upload fingerprint gate fails before Play submission; the team quarantines the artifact, fixes secret mapping in a protected branch, rebuilds from the same reviewed commit, verifies expected SHA-256/fingerprint/versionCode, and uploads the corrected AAB to an internal track. A test of the signing task prevents staging credentials from being selected for prod.

## Trade-offs and decision criteria

Stopping release may delay a feature but protects update identity. If Play rejected the artifact, there may be no user exposure; if accepted or distributed, use Play controls and customer-impact assessment. Key reset is for lost/compromised upload credentials, not a routine workaround for one misconfigured job.

## Failure modes

Team retries the same wrong-key artifact repeatedly. A developer manually signs outside CI with no provenance. Upload and app-signing fingerprints are confused. A key is replaced in secrets but release jobs still cache old configuration. VersionCode is reused after an accepted upload, blocking correction.

## Production perspective

Enforce pre-upload certificate fingerprint and artifact-hash gates, protect environment-specific credentials, and log release state transitions. Rehearse wrong-key and compromise procedures; maintain Play Console access and upload-key recovery owners.

## Interview answer — short

“I halt promotion, determine upload/distribution state, compare the AAB certificate to the registered upload key, then rebuild through protected CI and verify before retrying.”

## Interview answer — structured

“First I contain the artifact and establish whether Play rejected it or users received anything. I record its hash and fingerprint, distinguish upload key from Play's app-signing key, and identify the CI secret/config path that selected the wrong one. I correct that path in a protected job, produce a new verified AAB with valid versionCode, and test on an internal track. If a credential is compromised or a bad release was distributed, I invoke the relevant incident and rollout process.”

## Interview answer — deep senior

“My response depends on the release state. I stop the pipeline and preserve the wrong-signed AAB hash, certificate fingerprint, source revision and CI logs without exposing secrets. If Play rejected the upload, users are not affected by that artifact; I fix the protected signing job and verify it selects the registered upload key. Under Play App Signing I do not confuse this with the app-signing key used for delivered APKs. I rebuild or re-sign only through an audited, reproducible pipeline, verify certificate, versionCode and hash before upload, and validate through an internal track before resuming promotion. I also check whether the artifact had been accepted on another channel or whether a key was compromised; those require containment, access review, possibly upload-key reset and rollout controls rather than a simple retry. I add a pre-upload fingerprint gate and an environment mapping test so prod can never silently select staging credentials. I do not modify bytes in a signed bundle or create an opaque local emergency artifact. The incident record ties the correction to one immutable binary and explains user impact accurately.”

## Deep-dive talking points

Discuss rejected versus distributed state, key roles, fingerprints, versionCode, protected rebuild and incident response.

## Follow-up questions

- Does a wrong upload key always reach users? **Answer:** no; Play may reject it before distribution.
- Which fingerprint should a pre-upload gate compare? **Answer:** the AAB upload certificate against the registered upload key.
- When might upload-key reset be appropriate? **Answer:** if the key is lost or compromised, following Play's current process.

## Self-check rubric

Classify exposure, preserve evidence, correct protected signing and add a preventive gate.

## References and reviewed-on date

- [Sign your app](https://developer.android.com/studio/publish/app-signing) — key roles and reset.
- [Upload an App Bundle](https://developer.android.com/studio/publish/upload-bundle) — submission workflow.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Play acceptance state must be confirmed in the real incident.
A release bundle was signed with the wrong key. How do you contain it and correct the pipeline?
