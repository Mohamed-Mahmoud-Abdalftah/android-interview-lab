---
id: "CIC-11"
question: "How do you automate versioning, changelog, and tagging?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "B"
phase: 4
priority: "P2"
order: 430
editorial_status: "reviewed"
---

# CIC-11

## Original interview question

How do you automate versioning, changelog, and tagging?

## What the interviewer evaluates

- VersionCode uniqueness, changelog provenance and tag timing.
- Avoiding tags for unshipped or rebuilt artifacts.

## Explanation in Arabic

Versioning automation لازم تربط كل release بـcommit وartifact. `versionCode` يزيد ولا يتكرر لتطبيق Play، `versionName` للعرض، changelog يتولد من merged PRs مع مراجعة بشرية للمعنى، وtag يتعمل بعد تثبيت artifact/قبول release حسب policy. ما نوسمش branch tip وبعدين نبني binary مختلف.

## Practical walkthrough

Versioning مش مجرد زيادة رقم تلقائي. في Android `versionCode` لازم يتقدم للنسخة المنشورة ضمن نفس package، و`versionName` للمستخدم، وrelease notes تشرح behavior والتغييرات المؤثرة. خلي tag يشير للـcommit الذي خرج منه الـAAB فعلًا، وخزّن digest وmapping. لو hotfix من branch قديم، لازم pipeline تمنع تكرار versionCode أو tag باسم موجود. changelog من PR titles وحدها ممكن يخفي migration أو permission جديدة؛ راجعه مع product وQA.

## Why it matters and how it works

Gradle produces variant metadata; CI can derive versionCode from a release sequence rather than wall clock. A Git tag names a commit, not an artifact by itself, so release manifest should include AAB hash and mapping file. Changelog entries must distinguish internal changes from user-facing behavior.

## Worked example

For `2.4.0`, CI reserves a unique versionCode, builds productionRelease from SHA X, runs checks, stores AAB hash, uploads internal, then creates an annotated release tag linked to X and artifact metadata after approval. A failed upload does not become a “released” tag.

## Trade-offs and decision criteria

Automated semantic versioning reduces manual mistakes but can misclassify breaking API or user-visible changes. Human review of release notes remains useful. Monotonic build numbers may have gaps; that is safer than reuse.

## Failure modes

Two parallel pipelines choose same versionCode and one upload fails. Use central reservation/serialized release job. Tagging before tests pass creates misleading release history.

## Production perspective

Release manifest and changelog include migrations, feature gates and rollback notes. CI verifies tag-to-artifact SHA and Play track status.

## Interview answer — short

“Automate unique versionCode, reviewed changelog and traceable tags tied to a tested artifact. The tag and release manifest should identify the exact commit and AAB hash.”

## Interview answer — structured

“I separate machine identity from user label: versionCode must be unique/monotonic for Play, while versionName communicates release. CI reserves the code, builds one artifact from a known SHA, generates draft notes from PRs and has a human review important changes. I tag the source commit only after release criteria are met and record the artifact hash/mapping. Parallel release jobs must not reuse a code.”

## Interview answer — deep senior

“I automate the mechanics but retain a clear release decision. A version code identifies an Android update ordering, while a version name is a user-facing label; I never derive either from an unverified local clock or an unprotected branch. The release job assigns a unique code, builds from a protected commit or tag, and records the artifact digest and mapping file with that identity. A changelog assembled from merged changes is a draft, not the final explanation: I review migrations, permissions, SDK changes and user-visible behavior with the team. For a hotfix cut from an older branch I still need a code greater than the published one and a tag pointing to the actual source. I prevent duplicate tags and version codes in CI, and I test the update path rather than only clean install. This is primarily traceability: when crash reports arrive, I should be able to answer exactly which code, signing identity and release notes reached users.”

## How to answer in the interview

- **Why:** a release must be uniquely traceable.
- **How:** bind version, tag, digest and mapping to one commit.
- **Trade-off:** automation speed versus review of user impact.
- **Failure case:** hotfix reuses a published version code.
- **Production solution:** gate uniqueness and test upgrade.

## Deep-dive talking points

Prompt for code/name distinction, parallel reservation, tag timing and artifact hash.

## Follow-up questions

- [CIC-03](../cic-03/): What must a release manifest store? **Answer:** source SHA, AAB hash, mapping and track.
- [CIC-14](../cic-14/): What belongs in release notes? **Answer:** changes and operational risks/rollback context.

## Self-check rubric

Define a monotonic versionCode source, generate release notes from reviewed changes and tag the exact shipped commit/artifact. Explain how to correct an incorrect tag without rewriting release history.

## References and reviewed-on date

- [Android versioning](https://developer.android.com/studio/publish/versioning) — versionCode/versionName rules.
- [Gradle build variants](https://developer.android.com/build/build-variants) — variant output.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
