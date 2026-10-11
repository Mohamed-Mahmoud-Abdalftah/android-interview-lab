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

“I design release metadata for incident reconstruction. Given a crash, we must find the exact AAB, mapping, native symbols, dependencies, source SHA and Play track. A Git tag alone is insufficient if the artifact was rebuilt after tagging. I serialize or centrally allocate versionCode, validate production flavor, produce a reviewed changelog with risk notes, and record whether the version was uploaded, staged or fully rolled out. Failed candidates retain their own identity rather than being silently reused. Use central reservation/serialized release job.”

## Deep-dive talking points

Prompt for code/name distinction, parallel reservation, tag timing and artifact hash.

## Follow-up questions

- [CIC-03](../cic-03/): What must a release manifest store? **Answer:** source SHA, AAB hash, mapping and track.
- [CIC-14](../cic-14/): What belongs in release notes? **Answer:** changes and operational risks/rollback context.

## Self-check rubric

Can you explain the mechanism, apply the example, justify a trade-off, identify a failure mode, and answer both follow-ups?

## References and reviewed-on date

- [Android versioning](https://developer.android.com/studio/publish/versioning) — versionCode/versionName rules.
- [Gradle build variants](https://developer.android.com/build/build-variants) — variant output.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
