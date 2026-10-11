---
id: "CIC-03"
question: "What are build artifacts and release tracks?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "A"
phase: 4
priority: "P2"
order: 422
editorial_status: "reviewed"
---

# CIC-03

## Original interview question

What are build artifacts and release tracks?

## What the interviewer evaluates

- APK/AAB, mappings, test reports and provenance.
- Internal/closed/open/production tracks and artifact promotion.

## Explanation in Arabic

Build artifact هو الناتج القابل للتوزيع أو التشخيص: APK للتثبيت، AAB لـPlay delivery، mapping file لفك obfuscated crashes، native symbols وتقارير tests. Release tracks في Play بتحدد مين يستقبل النسخة: internal، closed، open أو production. المهم نفس artifact المجرّب يترقّى، مع versionCode فريد وsigning صحيح.

## Why it matters and how it works

An AAB is a publishing format from which Google Play serves device-specific APKs. Tracks control audience and rollout, not source branches. Mapping/native symbols must match the exact binary for useful crash analysis.

## Worked example

Build AAB from commit X, store SHA-256, mapping and test evidence; upload to internal testing, run smoke tests, then promote the same version to a small production percentage. If a regression appears, halt rollout and fix-forward under platform constraints.

## Trade-offs and decision criteria

Internal track speeds feedback but has narrower device coverage. Production staged rollout reduces blast radius but cannot undo updates already installed; plan backend feature gates and data migration compatibility.

## Failure modes

Rebuilding a “same version” from a different commit invalidates test evidence and mapping. Uploading debug APK instead of release AAB misses R8/ABI behavior. Preserve immutable artifact identity.

## Production perspective

Release manifest links commit, variant, versionCode, signing identity, artifact hash, mapping and track history. Telemetry segments crashes and payment failures by version/device cohort.

## Interview answer — short

“Artifacts include APK/AAB and matching diagnostic outputs. Play tracks control release audience; I promote a traceable, tested artifact rather than rebuild between stages.”

## Interview answer — structured

“I distinguish installable APK from the AAB used for Play distribution, and retain R8 mapping/native symbols for exact crash retracing. Internal, closed and open tracks expose builds to progressively broader testers before production. I record commit, variant, versionCode and artifact hash, then promote the same version. Staged production rollout monitors crashes and business metrics; halting rollout does not remove an already installed bad version.”

## Interview answer — deep senior

“I treat the artifact as the unit of evidence. Tests, mapping, native symbols, dependency manifest and signing metadata all refer to its hash. Play may generate split APKs from an AAB, so I smoke-test delivered variants for ABI-sensitive SDKs. Tracks are audience controls, not security guarantees; testers may still hit real backends if environments are misconfigured. A rollback strategy accounts for existing installations and irreversible schema changes, often using server-side gates plus a compatible fix-forward release. Preserve immutable artifact identity.”

## Deep-dive talking points

Prompt for AAB/splits, matching mapping, immutable promotion, installed-version rollback limit.

## Follow-up questions

- [CIC-10](../cic-10/): How publish internal build? **Answer:** upload a signed release artifact to selected Play track.
- [CIC-14](../cic-14/): What does halt rollout do? **Answer:** stops further distribution, not uninstall existing copies.

## Self-check rubric

Can you explain this decision, apply the example, name a trade-off and failure, and answer both follow-ups without relying on a memorized slogan?

## References and reviewed-on date

- [Android App Bundle](https://developer.android.com/guide/app-bundle) — distribution format.
- [Play publishing overview](https://developer.android.com/studio/publish) — release tracks.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
