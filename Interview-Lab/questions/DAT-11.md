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

## Practical walkthrough

migration مش `version++` وخلاص. اعرف كل schema اتحطت في release للمستخدمين، ومين ممكن يعمل upgrade مباشر من v1 لـv5؛ اكتب migration path كاملة. لو أضفت non-null column، default لازم يحافظ على meaning مش بس يعدّي schema validation. لو split table، انقل rows وforeign keys/indices وخطط لو app مات أثناء migration؛ SQLite transaction غالبًا تحمي schema change المحلية لكن test ضروري. export schema JSON للversion control، استخدم Room migration tests على old files فيها nulls/edge rows، وقارن counts وbusiness invariants. `fallbackToDestructiveMigration` لا تستخدمها لبيانات المستخدم المهمة لمجرد build ناجح.

## Trade-offs and decision criteria

Auto migration reduces boilerplate for straightforward changes; manual migration gives control for transforms. A destructive fallback is acceptable only when data is explicitly disposable and product agrees. Preserve compatibility with old app/backend contracts during staged rollout.

## Failure modes

Adding a NOT NULL column without default fails on existing rows. Renaming a field without copying data loses content. A migration tested only from version N-1 misses users upgrading after months offline.

## Production perspective

A notes app exports schema history, tests upgrades from every shipped version with drafts and large rows, then stages release and monitors migration crashes. It backs up critical user content and provides recovery if disk space is insufficient.

## Interview answer — short

“I preserve exported schemas, implement every supported upgrade path and test migrations against old databases with real data. I avoid destructive fallback for user-owned data and monitor rollout for migration failures.”

## Interview answer — structured

“A safe Room migration begins with the versions that real users may have, not only the last release. I export schemas, write auto or manual migrations, and test old database files containing nulls, duplicates and large datasets. Room validates the resulting schema, but tests also assert row counts and semantic values. A destructive fallback is unacceptable for offline drafts. I consider startup time, disk-full behavior and staged rollout so a failure can be detected before broad impact.”

## Interview answer — deep senior

Migration is a data-preservation operation under mobile failure conditions. I inventory shipped schemas and upgrade paths, choose auto migration only for changes it can express safely, and write manual transforms for data reshaping. Tests build databases at each supported old version, populate representative and adversarial rows, run the full path, and compare both schema and business invariants. I avoid wiping user data as a convenience, plan for low storage and process interruption, and monitor crash reports by old/new version during staged rollout. I also coordinate backend compatibility because users can stay on old app versions while data/server contracts change. For very risky encryption or file moves, I use a verified copy-and-swap protocol with recovery markers. Room validates expected schema after migration.

I inventory every database version shipped to real users and test upgrades from each supported one, not only the immediately previous schema. Adding a non-null field may be syntactically easy but needs a business-correct default for old rows; splitting a table requires backfill, indices, and foreign-key checks. Room’s exported schemas and migration test helper make those paths reproducible. I would test representative and adversarial rows, kill/restart around upgrade where feasible, and verify that user-visible counts and ownership are unchanged. A destructive fallback might be acceptable only for explicitly disposable cache, never as a silent fix for orders or drafts. I also stage rollout and watch migration crashes before wide release.

## How to answer in the interview

- **Why:** A schema upgrade is a user-data preservation operation.
- **How:** Inventory shipped versions, export schemas, backfill and test full paths.
- **Trade-offs:** Use auto migration only for transformations it expresses safely.
- **Failure cases:** Wrong default, missing upgrade path, destructive fallback.
- **Production solution:** Representative old DB fixtures, invariant checks and staged rollout.

## Deep-dive talking points

Cover old-version matrix, row-level assertions, storage failure and staged rollback limits.

## Follow-up questions

- [DAT-06](../dat-06/): What validates schema? **Answer:** Room migration/schema verification plus tests of actual values.
- [DAT-22](../dat-22/): How migrate encrypted stores? **Answer:** copy/verify/swap with key and crash recovery planning.

## Self-check rubric

Can I enumerate shipped versions, protect rows, reject destructive fallback and test low-storage failure?

## References and reviewed-on date

- [Android Room migrations](https://developer.android.com/training/data-storage/room/migrating-db-versions) — migration and testing guidance.

Technically reviewed against linked primary documentation on 2026-10-13. Examples are conceptual unless explicitly stated otherwise; no Android device execution is claimed.
