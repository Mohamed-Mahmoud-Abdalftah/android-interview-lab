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

“I assume a malicious PR can modify Gradle scripts, tests and workflow inputs. Therefore privileged jobs never check out and execute unreviewed PR code, even if secret values are masked in CI output. I use protected environments, least-privilege short-lived service credentials where possible, audited approvals and separate artifact promotion. Signing identity, upload key and Play service account have distinct compromise paths and rotation playbooks. Reproducible hashes tie tests to the signed release, and operational monitoring detects unauthorized track activity.”

## Deep-dive talking points

Prompt for malicious Gradle script, PR versus release isolation, Play upload key, audit and rotation.

## Follow-up questions

- [CIC-18](../cic-18/): How can PR steal secrets? **Answer:** execute code in privileged workflow context.
- [CIC-03](../cic-03/): What ties release to source? **Answer:** artifact hash, commit and signing provenance.

## Self-check rubric

Can you explain this decision, apply the example, name a trade-off and failure, and answer both follow-ups without relying on a memorized slogan?

## References and reviewed-on date

- [Play App Signing](https://developer.android.com/studio/publish/app-signing) — signing and upload key roles.
- [Android publishing](https://developer.android.com/studio/publish) — release workflow.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
