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

Room DAO test تثبت query، ordering، constraints وFlow observation على قاعدة فعلية مناسبة؛ mock DAO لا يثبت SQL. Migration test تبدأ من ملفات schema قديمة تمثل إصدارات مستخدمين حقيقية، تضيف rows فيها nulls وduplicates وUnicode وقيم حدودية، ثم تعمل migration للمستهدف وتفحص data وindexes وforeign keys. جرّب كل upgrade path مدعومة بدل آخر إصدار فقط.

## Practical walkthrough

Transaction test تُدخل write ثم exception قبل النهاية وتتأكد أن الاثنين لم يثبتا؛ لو rollback policy مختلفة وثّقها. الـin-memory DB مفيدة لاختبارات DAO قصيرة، لكنها لا تثبت durability بعد إغلاق العملية؛ استخدم file-backed/device integration حين يكون ده claim. لا تخلط نجاح `MigrationTestHelper` مع صحة business transformation بلا assertions على rows.

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

“I test Room at the real database boundary when the question is about SQL or durability. DAO tests insert representative rows and assert filtering, ordering, uniqueness and observed updates rather than mocking the DAO and replaying expected calls. For migrations I keep exported schemas and create fixtures from every supported old version, including messy customer data: null legacy fields, duplicate merchant IDs, Arabic names and long values. I run the upgrade path to the release schema and assert transformed rows, indexes, foreign keys and the documented conflict-resolution rule. A schema validation pass alone may miss the wrong row being chosen. For transactions I inject a failure after the first write and assert the invariant that either all related rows commit or none do. I distinguish in-memory test convenience from file durability and process restart. If the release includes a risky migration, I run a device or emulator test with a file-backed database and a minified release-like build. A test that starts only from a fresh schema cannot protect existing users.”

## How to answer in the interview

- **Why:** old customer data is where schema changes fail.
- **How:** create versioned fixtures, migrate and assert rows, indexes and rollback.
- **Trade-off:** in-memory speed versus file/device durability evidence.
- **Failure case:** schema validation passes while duplicate rows merge incorrectly.
- **Production solution:** release-like migration matrix from every supported version.

## Deep-dive talking points

Prompt for exported schemas, realistic old rows, all upgrade paths, rollback and remote boundary.

## Follow-up questions

- [TST-22](../tst-22/): How get fixtures? **Answer:** synthesize from anonymized production shapes and boundary cases.
- [TST-20](../tst-20/): Does Room transaction prevent double charge? **Answer:** no; server idempotency is separate.

## Self-check rubric

Create an old schema fixture with edge-case rows, run each supported Room migration path, assert rows/indexes/foreign keys, and inject an exception inside a transaction to prove rollback. Name the Android runtime needed.

## References and reviewed-on date

- [Room migration testing](https://developer.android.com/training/data-storage/room/migrating-db-versions) — MigrationTestHelper and schemas.
- [Room withTransaction API](https://developer.android.com/reference/kotlin/androidx/room/package-summary) — local transactions.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
