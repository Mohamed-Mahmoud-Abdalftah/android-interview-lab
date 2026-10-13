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

### Practical walkthrough in Egyptian Arabic

الـartifact مش مجرد ملف نحمّله: AAB/APK، mapping file، native symbols، test reports، SBOM أو provenance لو مستخدمينها، وكلها مرتبطة بالـcommit والـvariant والـversionCode. Internal track للتجربة داخل الفريق، closed/open testing لشرائح أوسع، production rollout تدريجي. الخطأ الشائع إنك تعيد build عند كل track فتتغير البايتات؛ الأفضل تروّج نفس الـartifact الذي اختبرته. لو ظهر crash، لازم تقدر تحدد أي mapping وsource أنتج النسخة فعلاً.

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

“A build artifact is the immutable output I can identify and promote: for Android that is commonly an AAB or APK plus its R8 mapping, native symbols and test evidence. I attach commit, variant, version code and artifact digest so crash reports can be retraced to the correct build. Release tracks determine who can install the artifact: internal testers first, then broader test audiences, then staged production according to policy. A track is distribution scope, not a different source tree. I prefer promoting the same verified AAB rather than rebuilding for each track, because rebuilding can change dependencies, resources or signing output and invalidate prior testing. If a release-only native crash appears, I need the exact bundle and symbols from that rollout, not merely a nearby branch. The trade-off is storage and metadata discipline, but it makes incident containment and audit feasible. Before promotion I check package ID, version code, signing identity and target audience explicitly.”

## How to answer in the interview

- **Why:** release evidence must map to exact bytes.
- **How:** attach commit, variant, digest, mapping and track.
- **Trade-off:** artifact retention versus reproducible incident analysis.
- **Failure case:** wrong mapping makes crash stack unreadable.
- **Production solution:** promote one verified AAB and keep provenance.

## Deep-dive talking points

Prompt for AAB/splits, matching mapping, immutable promotion, installed-version rollback limit.

## Follow-up questions

- [CIC-10](../cic-10/): How publish internal build? **Answer:** upload a signed release artifact to selected Play track.
- [CIC-14](../cic-14/): What does halt rollout do? **Answer:** stops further distribution, not uninstall existing copies.

## Self-check rubric

Name the AAB/APK, mapping file, symbols and test reports as versioned artifacts; distinguish internal, closed, open and production tracks; explain how one artifact retains provenance.

## References and reviewed-on date

- [Android App Bundle](https://developer.android.com/guide/app-bundle) — distribution format.
- [Play publishing overview](https://developer.android.com/studio/publish) — release tracks.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
