---
id: "DAT-11"
question: "How do you design a migration that preserves user data?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "B"
phase: 3
priority: "P1"
order: 268
editorial_status: "reviewed"
---

# DAT-11

## Original interview question

How do you design a migration that preserves user data?

## What the interviewer evaluates

Plan data-preserving Room migration with shipped schemas and failure recovery.

## Explanation in Arabic

Migration بتغيّر schema قديمة إلى جديدة من غير ما نمسح user data. نحتفظ بـexported schemas لكل release، ونبني migration paths من versions المدعومة، ونختبرها بقاعدة فيها rows حقيقية/edge cases. `fallbackToDestructiveMigration` مش حل افتراضي لتطبيق عنده offline drafts؛ ده ممكن يمسحها. للعمليات الكبيرة نحتاج مساحة disk، rollback plan ومراقبة crash في rollout.

## Why it matters and how it works

Room validates expected schema after migration. Auto migrations can handle supported structural changes; manual SQL/data transforms need explicit code and tests. Migrations run before the app can use the database, so long work delays startup. Backup and staged rollout matter for irreversible schema changes.

## Worked example

Conceptual manual migration (Room API version must match project); SQL example adds a non-null column with safe default.

```kotlin
import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase

val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(db: SupportSQLiteDatabase) {
        db.execSQL("ALTER TABLE notes ADD COLUMN synced INTEGER NOT NULL DEFAULT 0")
    }
}
```

## Trade-offs and decision criteria

Auto migration reduces boilerplate for straightforward changes; manual migration gives control for transforms. A destructive fallback is acceptable only when data is explicitly disposable and product agrees. Preserve compatibility with old app/backend contracts during staged rollout.

## Failure modes

Adding a NOT NULL column without default fails on existing rows. Renaming a field without copying data loses content. A migration tested only from version N-1 misses users upgrading after months offline.

## Production perspective

A notes app exports schema history, tests upgrades from every shipped version with drafts and large rows, then stages release and monitors migration crashes. It backs up critical user content and provides recovery if disk space is insufficient.

## Interview answer — short

“I preserve exported schemas, implement every supported upgrade path and test migrations against old databases with real data. I avoid destructive fallback for user-owned data and monitor rollout for migration failures.”

## Interview answer — structured

“A safe Room migration begins with the versions that real users may have, not only the last release. I export schemas, write auto or manual migrations, and test old database files containing nulls, duplicates and large datasets. Room validates the resulting schema, but tests also assert row counts and semantic values. A destructive fallback is unacceptable for offline drafts. I consider startup time, disk-full behavior and staged rollout so a failure can be detected before broad impact. Auto migration reduces boilerplate for straightforward changes; manual migration gives control for transforms. A destructive fallback is acceptable only when data is explicitly disposable and product agrees. Preserve compatibility with old app/backend contracts during staged rollout. A notes app exports schema history, tests upgrades from every shipped version with drafts and large rows, then stages release and monitors migration crashes.”

## Interview answer — deep senior

“Migration is a data-preservation operation under mobile failure conditions. I inventory shipped schemas and upgrade paths, choose auto migration only for changes it can express safely, and write manual transforms for data reshaping. Tests build databases at each supported old version, populate representative and adversarial rows, run the full path, and compare both schema and business invariants. I avoid wiping user data as a convenience, plan for low storage and process interruption, and monitor crash reports by old/new version during staged rollout. I also coordinate backend compatibility because users can stay on old app versions while data/server contracts change. For very risky encryption or file moves, I use a verified copy-and-swap protocol with recovery markers. Room validates expected schema after migration. Auto migrations can handle supported structural changes; manual SQL/data transforms need explicit code and tests. Migrations run before the app can use the database, so long work delays startup. Backup and staged rollout matter for irreversible schema changes. Adding a NOT NULL column without default fails on existing rows. Renaming a field without copying data loses content. A migration tested only from version N-1 misses users upgrading after months offline. A notes app exports schema history, tests upgrades from every shipped version with drafts and large rows, then stages release and monitors migration crashes.”

## Deep-dive talking points

Cover old-version matrix, row-level assertions, storage failure and staged rollback limits.

## Follow-up questions

- [DAT-06](../dat-06/): What validates schema? **Answer:** Room migration/schema verification plus tests of actual values.
- [DAT-22](../dat-22/): How migrate encrypted stores? **Answer:** copy/verify/swap with key and crash recovery planning.

## Self-check rubric

Can I enumerate shipped versions, protect rows, reject destructive fallback and test low-storage failure?

## References and reviewed-on date

- [Android Room migrations](https://developer.android.com/training/data-storage/room/migrating-db-versions) — migration and testing guidance.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
