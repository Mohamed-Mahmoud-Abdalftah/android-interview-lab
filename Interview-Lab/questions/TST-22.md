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

Migration اللي تنجح على empty DB ممكن تقع عند مستخدم قديم عنده null، duplicate key، Unicode، rows كثيرة أو enum قديم. نحتفظ exported schemas للإصدارات المنشورة، ونبني fixtures synthetic من شكل بيانات anonymized/aggregated من production من غير نسخ بيانات شخصية. نختبر upgrade من كل version مدعومة ونراجع constraints ونتائج التحويل.

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

“A migration is a function over every database shape allowed by previous releases, not just an empty schema. I keep exported Room schemas, create fixtures with realistic boundaries and use MigrationTestHelper to upgrade from each supported version. I assert row content, indexes, foreign keys and no unintended loss. Production aggregates and incidents guide fixture design, but CI should not contain raw customer records. The mechanics matter. MigrationTestHelper can create an older schema and run migration. Fixtures should vary nullability, uniqueness, foreign-key integrity, ordering and large data volume. Production shape metrics can guide distribution, but direct customer data must be excluded or properly de-identified under policy. The choice has a trade-off. Synthetic fixtures protect privacy and target boundaries but may miss unseen production combinations. Controlled anonymized data can improve realism with governance; avoid raw user DBs in developer laptops or CI.”

## Interview answer — deep senior

“I inventory old constraints and data distributions before writing migration SQL. If a new unique index meets legacy duplicates, the migration needs an explicit conflict-resolution rule that tests can verify. Fixtures cover partial writes from old versions, nullable fields, non-ASCII text, large row counts and data combinations tied to prior bugs. I test every direct upgrade path to current version, reopen the DB and run representative queries. Privacy-safe synthetic generation lets CI reproduce defects; performance and rollback risks are reported separately. Consider a concrete case. If v1 allowed duplicate merchant IDs and v3 adds unique index, fixture includes duplicates and specifies deterministic merge rule. Test migration v1→v3 and v2→v3, then assert row count, chosen canonical merchant and foreign keys. Add Unicode Arabic names and long text. A failure case illustrates the risk. A migration test uses only one pristine row, passes, then index creation fails on legacy duplicates. Make fixtures from schema-history and incident patterns, and test no destructive fallback silently loses payment history. In production, the response is concrete. CI archives schema JSON for each release, validates all upgrade paths on representative devices, and measures migration time for large fixture DBs. Rollback planning acknowledges schema changes may be one-way.”

## Deep-dive talking points

Prompt for exported schemas, production shape not raw PII, duplicate resolution, all upgrade paths and performance.

## Follow-up questions

- [TST-11](../tst-11/): What tool tests old Room schemas? **Answer:** MigrationTestHelper with exported schemas.
- [CIC-14](../cic-14/): Why stage migration release? **Answer:** detect data-shape failures before full rollout.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Room migration testing](https://developer.android.com/training/data-storage/room/migrating-db-versions) — exported schemas and helper.
- [Room migration overview](https://developer.android.com/training/data-storage/room/migrating-db-versions) — migration paths.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
