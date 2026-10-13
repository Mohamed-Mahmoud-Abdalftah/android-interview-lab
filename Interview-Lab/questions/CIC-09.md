---
id: "CIC-09"
question: "How do you protect signing material and CI secrets?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "B"
phase: 4
priority: "P2"
order: 428
editorial_status: "reviewed"
---

# CIC-09

## Original interview question

How do you protect signing material and CI secrets?

## What the interviewer evaluates

- Signing key custody and PR secret isolation.
- Short-lived credentials, audit and artifact provenance.

## Explanation in Arabic

Android signing key لو اتسرب attacker يقدر يوقّع artifacts حسب منظومة التوزيع؛ CI secrets زي Play API credentials برضه خطيرة. نخلي release signing في protected job/environment، صلاحيات أقل ما يمكن، approvals/audit، وuntrusted PR/fork jobs من غير secrets. ما نطبعش قيم في logs أو artifacts، ونستخدم managed key storage/Play App Signing حسب release setup.

## Practical walkthrough

Signing key وPlay credentials أسرار نشر، مش input لأي PR. خزنها في secret manager أو protected CI environment بمبدأ أقل صلاحية، وحدد من يقدر يشغّل release job ومن يقدر يوافقه. استخدم ephemeral/OIDC credentials لو provider يدعم، وراجع log masking لأنه مش يمنع كل تسريب؛ PR خبيث ممكن يبعث السر للشبكة لو job شغّل كوده بنفس الصلاحيات. اعمل rotation/revocation plan وتابع audit logs، وافصل upload key عن app signing key حسب نموذج Play.

## Why it matters and how it works

Play App Signing separates app signing key management from upload key workflows. CI credentials are granted only to trusted release jobs after required checks, with scoped access and rotation. A masked CI variable is not safe if attacker-controlled code can read it and exfiltrate it.

## Worked example

A fork PR runs compile/tests with read-only token. Only after merge to protected branch does a separate release workflow fetch upload credentials, sign AAB and upload to internal track. The job records artifact hash but never exposes keystore bytes or passwords in logs.

## Trade-offs and decision criteria

Cloud-managed signing reduces direct key handling but adds provider dependency. Manual signing limits automation but can create human error. Choose a custody model with recovery and upload-key rotation procedures.

## Failure modes

Using `pull_request_target` to check out untrusted PR code and run Gradle with repository secrets leaks credentials. Split contexts and never execute untrusted build scripts in privileged job.

## Production perspective

Periodic audit reviews who can trigger release, secret access logs, credential expiry and artifact signatures. Incident runbook covers upload-key compromise and revoked Play service credentials.

## Interview answer — short

“I isolate signing and Play credentials in protected release jobs. Untrusted PR code runs without secrets; masking alone cannot prevent exfiltration from a malicious build script.”

## Interview answer — structured

“I keep the signing pipeline separate from ordinary PR checks. Fork code is untrusted and gets read-only permissions, no keystore or Play API credentials. A protected merge/release job retrieves scoped secrets, signs the exact tested AAB and records provenance. Play App Signing and upload-key recovery are considered in the custody plan. Logs and artifacts are scanned for accidental leakage.”

## Interview answer — deep senior

“My main rule is a trust boundary: a workflow that executes untrusted pull-request code must never receive signing material or publishing credentials. A secret mask in logs is not a security boundary; code with the secret can send it elsewhere. I use protected branches and environments, minimal token permissions, limited reviewers for promotion and separate release jobs that check out a trusted ref. Where supported, short-lived federated credentials reduce stored long-lived secrets. For Android I distinguish the upload key used by our pipeline from the app signing key held under Play App Signing; their recovery and compromise paths differ. I restrict artifact and mapping access too, keep audit logs, and rehearse revocation/rotation. An attacker can hide exfiltration in a build script or dependency, so dependency verification and careful workflow review matter alongside encrypted secret storage. The trade-off is a few controlled steps in the release path for a much smaller blast radius.”

## How to answer in the interview

- **Why:** release credentials can publish hostile builds.
- **How:** isolate trusted release job and least-privilege secrets.
- **Trade-off:** convenience versus blast radius.
- **Failure case:** fork PR build script exfiltrates secret.
- **Production solution:** protected environments, short-lived credentials, rotation.

## Deep-dive talking points

Prompt for malicious Gradle script, PR versus release isolation, Play upload key, audit and rotation.

## Follow-up questions

- [CIC-18](../cic-18/): How can PR steal secrets? **Answer:** execute code in privileged workflow context.
- [CIC-03](../cic-03/): What ties release to source? **Answer:** artifact hash, commit and signing provenance.

## Self-check rubric

Keep signing credentials out of untrusted PR jobs, scope and rotate secrets, protect workflow permissions and review fork behavior. Explain what a malicious PR could read if the boundary is wrong.

## References and reviewed-on date

- [Play App Signing](https://developer.android.com/studio/publish/app-signing) — signing and upload key roles.
- [Android publishing](https://developer.android.com/studio/publish) — release workflow.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
