---
id: "TST-11"
question: "How do you test Room DAOs, database migrations, and transactions?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 406
editorial_status: "reviewed"
---

# TST-11

## Original interview question

How do you test Room DAOs, database migrations, and transactions?

## What the interviewer evaluates

- Real DAO query and migration validation with historical schemas.
- Transaction rollback and process recreation behavior.

## Explanation in Arabic

Room DAO tests لازم تستخدم database حقيقية في test عشان SQL وconstraints وFlow invalidation. Migration tests تبدأ من schema قديمة فعلًا وبيانات تمثل مستخدمين قدام، ثم تشغل migration وتتحقق من rows/indexes/nullability. Transaction test يفشل في النص ويتأكد إن كل writes اتراجعت. Fake DAO ما يثبتش دي.

## Why it matters and how it works

Room compiles DAO queries but runtime behavior, SQLite constraints and schema migration still need execution. Exported schema files and MigrationTestHelper let tests create an older version and run a migration path. `withTransaction` guarantees local atomicity unless the block fails/cancels.

## Worked example

Create v1 DB with a nullable legacy account row and duplicate historical values, then migrate to v3. Assert transformed rows, indexes and foreign keys. In a separate test, insert payment status and reversal row in one transaction, throw before completion, and assert neither persisted.

## Trade-offs and decision criteria

In-memory DB tests are fast but do not cover file persistence or power loss. File-backed instrumentation tests better exercise reopen and migration. Keep both where justified; migration fixtures should include edge cases from production shapes without personal data.

## Failure modes

A migration passes on empty DB but fails on null/duplicate rows from old releases. Keep exported schemas for every shipped version and generate boundary fixtures. Do not edit old schema artifacts to make tests pass.

## Production perspective

CI runs DAO and all-upgrade-path migrations against representative Android/SQLite versions. Release checks inspect destructive migration policy and backup/restore behavior.

## Interview answer — short

“I test DAOs against real Room/SQLite, migrations from exported historical schemas with realistic rows, and transaction rollback on failure. A fake repository cannot prove SQL or durability.”

## Interview answer — structured

“DAO tests execute real queries and constraints. Migration tests use old schema versions and nontrivial data, run the migration, and assert both content and schema. I test transaction rollback by forcing a failure after one write. In-memory DB is useful for speed, but file-backed reopen tests add persistence confidence. I keep exported schemas from released versions and avoid destructive migration unless data loss is an explicit product decision.”

## Interview answer — deep senior

“I treat migration as compatibility with the installed base, not just current schema validation. Fixtures cover nulls, duplicates, Unicode, large tables, old enum values and partially populated records, built from anonymized shapes rather than customer data. I run each supported upgrade path, verify indexes/foreign keys and inspect query plans for regressions. For payment status plus reversal intent, I assert atomic commit and rollback under exceptions/cancellation, then reopen a file-backed DB to verify state. None of this proves remote provider atomicity; reconciliation tests handle that gap.”

## Deep-dive talking points

Prompt for exported schemas, realistic old rows, all upgrade paths, rollback and remote boundary.

## Follow-up questions

- [TST-22](../tst-22/): How get fixtures? **Answer:** synthesize from anonymized production shapes and boundary cases.
- [TST-20](../tst-20/): Does Room transaction prevent double charge? **Answer:** no; server idempotency is separate.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Room migration testing](https://developer.android.com/training/data-storage/room/migrating-db-versions) — MigrationTestHelper and schemas.
- [Room withTransaction API](https://developer.android.com/reference/kotlin/androidx/room/package-summary) — local transactions.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
