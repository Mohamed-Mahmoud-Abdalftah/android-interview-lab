---
id: "SEC-25"
question: "What are OWASP MASVS/MASTG, and how do they guide mobile security reviews?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 322
editorial_status: "reviewed"
---

# SEC-25

## Original interview question

What are OWASP MASVS/MASTG, and how do they guide mobile security reviews?

## What the interviewer evaluates

- MASVS as controls and MASTG as test procedures.
- Risk-based scope, evidence and the difference between a checklist and proof.

## Explanation in Arabic

OWASP MASVS معيار controls لأمن mobile apps، وMASTG دليل عملي للاختبارات. نستخدمهم عشان نحدد requirements ونربط كل control باختبار ودليل، مش عشان نعمل checkboxes ونقول التطبيق “آمن”. نطاق fintech يركز على storage، crypto، network، authentication، platform وresilience حسب threat model.

## Practical walkthrough

في review لتطبيق POS، اربط MASVS-STORAGE بملفات token وbackup، وMASTG باختبار استخراج release APK والـrestore. سجل لكل control النتيجة والدليل ونوع الجهاز/API level والحد المتبقي. MASVS معيار requirements وMASTG طرق اختبار؛ مرور checklist آليًا لا يغطي backend authorization ولا يثبت إن الجهاز الحقيقي محمي من كل هجوم.

## Why it matters and how it works

MASVS defines verification areas and MASTG gives test methods; MASWE catalogs weaknesses. A review maps app assets and threats to relevant controls, executes tests on the actual release build and records evidence, severity and remediation. Passing a tool scan is not equivalent to passing all controls.

## Worked example

For a POS app, map a token-store design to MASVS-STORAGE and MASVS-CRYPTO, then test backup extraction, local file contents, key loss and logging. Map API traffic to MASVS-NETWORK and capture release traffic to verify TLS behavior. Record device/API and app version with findings.

## Trade-offs and decision criteria

A standard makes coverage repeatable, but each app has different assets and risk. A strict checklist can miss a payment-state logic bug; supplement it with architecture and business-flow threat modeling.

## Failure modes

A reviewer marks “encrypted” because a database library is present without testing backups or plaintext logs. Require evidence from runtime/file inspection and a recovery drill. Treat false positives and untested controls explicitly.

## Production perspective

Keep a control-to-test matrix in security review, run MASTG procedures against representative devices and minified builds, and track exceptions with owners and expiry. Retest after SDK, OS or backend changes.

## Interview answer — short

“MASVS states mobile security controls; MASTG explains how to test them. I map them to the app’s threat model, collect release-build evidence and record gaps rather than equating checklist completion with security.”

## Interview answer — structured

“I use MASVS to define expected security properties and MASTG to choose test procedures. For a fintech app that includes local storage, cryptography, authentication, network transport and tamper resilience. I map each relevant control to a concrete test on a release build, record evidence and risks, then fix and retest. I also threat-model business logic because a checklist cannot by itself catch duplicate payments or client-only authorization. ”

## Interview answer — deep senior

“I start from assets—tokens, transaction identity, card-adjacent data and financial authority—and enumerate realistic device and network attackers. I select MASVS controls that address those threats, then use MASTG methods to test actual APK, backend interactions, backups and telemetry. Each result has device/OS/build context, evidence and residual risk; automated tools are aids with false positives and false negatives. I pair this with adversarial payment-flow tests and security review of server trust boundaries. A ‘pass’ is scoped to tested behavior and time, not a perpetual certificate. A useful deliverable is a traceable matrix: asset, threat, MASVS control, MASTG procedure, release-build evidence, affected API levels, owner and residual risk. I would prioritize payment authority, token storage and cross-app entry points over cosmetic checklist coverage. Automated static findings are a starting point; dynamic tests and backend tests still matter. A green control result should describe what was actually tested and what remained out of scope.”

## How to answer in the interview

- **Why:** security reviews need testable requirements and evidence.
- **How:** map app assets to MASVS controls and MASTG procedures.
- **Trade-off:** broad coverage costs time, so prioritize high-risk paths.
- **Failure case:** checkbox completion without release-build evidence.
- **Production solution:** record scope, device matrix, findings, owners, and residual risk.

## Deep-dive talking points

Prompt for asset/threat inventory, control-to-test evidence, release APK, tool limits and business-logic coverage.

## Follow-up questions

- [SEC-23](../sec-23/): Which storage test matters? **Answer:** inspect backup and actual files, not just declarations.
- [SEC-27](../sec-27/): Can MASVS replace backend authorization review? **Answer:** no; test business state and ownership.

## Self-check rubric

Can I map a control to a concrete test and explain limits of scans/checklists?

## References and reviewed-on date

- [OWASP MASVS](https://mas.owasp.org/MASVS/) — mobile verification areas.
- [OWASP MASTG](https://mas.owasp.org/MASTG/) — testing guide.

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
