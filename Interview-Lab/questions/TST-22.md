---
id: "TST-22"
question: "A database migration fails only with old customer data. How do you generate realistic fixtures?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "C"
phase: 4
priority: "P1"
order: 417
editorial_status: "reviewed"
---

# TST-22

## Original interview question

A database migration fails only with old customer data. How do you generate realistic fixtures?

## What the interviewer evaluates

- Historical schema fixtures reflecting real data shapes.
- Privacy-safe generation and every supported upgrade path.

## Explanation in Arabic

Migration تفشل مع بيانات قديمة لأن fixture النظيفة لا تمثل الواقع. اجمع shape من schemas التاريخية وtelemetry آمنة بدون PII: null fields، duplicates، missing relations، Unicode/Arabic، long text، قيم enum قديمة. حدّد merge rule قبل الاختبار؛ لو v3 أضاف unique merchant ID والقديم فيه duplicates، مين الصف canonical وأين تذهب references؟ أنشئ DB لكل إصدار مدعوم، شغّل upgrade للمستهدف، ثم assert على row count، chosen values، indexes وforeign keys.

## Practical walkthrough

اختبر transaction rollback عند failure ولا تعتمد على “schema validation passed”. ممكن anonymized fixture لكن لا تنسخ بيانات عميل حقيقية إلى repo. بعد dry run على supported versions، نفّذ rollout تدريجي ورصد migration crash/OOM، وخطة recovery لا تفترض downgrade.

## Why it matters and how it works

MigrationTestHelper can create an older schema and run migration. Fixtures should vary nullability, uniqueness, foreign-key integrity, ordering and large data volume. Production shape metrics can guide distribution, but direct customer data must be excluded or properly de-identified under policy.

## Worked example

If v1 allowed duplicate merchant IDs and v3 adds unique index, fixture includes duplicates and specifies deterministic merge rule. Test migration v1→v3 and v2→v3, then assert row count, chosen canonical merchant and foreign keys. Add Unicode Arabic names and long text.

## Trade-offs and decision criteria

Synthetic fixtures protect privacy and target boundaries but may miss unseen production combinations. Controlled anonymized data can improve realism with governance; avoid raw user DBs in developer laptops or CI.

## Failure modes

A migration test uses only one pristine row, passes, then index creation fails on legacy duplicates. Make fixtures from schema-history and incident patterns, and test no destructive fallback silently loses payment history.

## Production perspective

CI archives schema JSON for each release, validates all upgrade paths on representative devices, and measures migration time for large fixture DBs. Rollback planning acknowledges schema changes may be one-way.

## Interview answer — short

“I use exported historical schemas and synthetic fixtures modeled on old customer data shapes: nulls, duplicates, Unicode, large tables and old enum values. I test every supported upgrade path and assert transformed data and constraints.”

## Interview answer — structured

“A migration is a function over every database shape allowed by previous releases, not just an empty schema. I keep exported Room schemas, create fixtures with realistic boundaries and use MigrationTestHelper to upgrade from each supported version. I assert row content, indexes, foreign keys and no unintended loss. Production aggregates and incidents guide fixture design, but CI should not contain raw customer records.”

## Interview answer — deep senior

“I reproduce the old data shape, not just the old table definition. I start from exported schemas and supported installed versions, then build fixtures with the kinds of rows that trigger real migrations: null legacy values, duplicate merchant identifiers, orphaned references, Arabic or Unicode names and long text. If a new unique index requires merging duplicates, the product and backend owners must decide the deterministic canonical-row rule before code is written. For each supported upgrade path I run the migration and assert row count, chosen values, foreign-key integrity, indexes and any derived totals. I also inject a failure mid-migration to verify transactional rollback or the documented recovery path. A helper that validates only the final schema cannot tell me whether the wrong customer row survived. I keep fixtures synthetic or anonymized, never raw customer records in source control. Before release I test on a device/emulator with a representative file-backed database and release-like build, stage the rollout, and watch migration failures by source version. A database downgrade after users have opened the new schema is not a safe automatic rollback plan.”

## How to answer in the interview

- **Why:** synthetic clean rows miss legacy data hazards.
- **How:** seed null, duplicate and Unicode cases for each supported schema path.
- **Trade-off:** more fixtures take maintenance but protect real migrations.
- **Failure case:** unique index fails or picks the wrong canonical row.
- **Production solution:** deterministic merge rule and staged rollout monitoring.

## Deep-dive talking points

Prompt for exported schemas, production shape not raw PII, duplicate resolution, all upgrade paths and performance.

## Follow-up questions

- [TST-11](../tst-11/): What tool tests old Room schemas? **Answer:** MigrationTestHelper with exported schemas.
- [CIC-14](../cic-14/): Why stage migration release? **Answer:** detect data-shape failures before full rollout.

## Self-check rubric

Seed every supported old schema with duplicate, null, Arabic/Unicode and long-text cases. Define the merge policy before migration and assert canonical rows, counts and foreign keys after each upgrade path.

## References and reviewed-on date

- [Room migration testing](https://developer.android.com/training/data-storage/room/migrating-db-versions) — exported schemas and helper.
- [Room migration overview](https://developer.android.com/training/data-storage/room/migrating-db-versions) — migration paths.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
