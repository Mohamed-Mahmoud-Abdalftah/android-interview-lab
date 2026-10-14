---
id: "SYS-13"
question: "How do you manage database migrations and backwards compatibility?"
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "B"
phase: 4
priority: "P1"
order: 342
editorial_status: "reviewed"
---

# SYS-13

## Original interview question

How do you manage database migrations and backwards compatibility?

## What the interviewer evaluates

Coordinate Room schema migration with backend compatibility and rollout windows.

## Explanation in Arabic

كيف تدير ترقيات قواعد البيانات (Database Migrations) والتوافقية العكسية (Backwards Compatibility) في Room دون فقدان بيانات المستخدمين؟

1. كيف تعمل الـ Migrations في Room؟
   - عند تعديل الـ Entity (إضافة عمود أو جدول جديد)، يجب زيادة رقم إصدار قاعدة البيانات (`version = 2`).
   - إذا فتح المستخدم التطبيق بعد التحديث ولم يجد كود هجرة (Migration) صريح، سينهار التطبيق فوراً برمي استثناء `IllegalStateException: Room cannot verify the data integrity`!
   - **كارثة ممنوعة في الإنتاج**: استخدام `fallbackToDestructiveMigration()`. هذا الأمر يقوم بمسح قاعدة البيانات بالكامل وتدمير كل بيانات المستخدم دون علمه!

2. أنواع الـ Migrations المتاحة:
   - **AutoMigration (AndroidX Room 2.4+)**: يتولى Room إنشاء كود الهجرة تلقائياً إذا كانت التغييرات بسيطة (إضافة عمود أو جدول جديد) باستخدام `@AutoMigration`.
   - **Manual Migration**: كتابة استعلامات SQL صريحة عبر `Migration(from, to)` للعمليات المعقدة (إعادة تسمية أعمدة، تقسيم جداول، أو تحويل أنواع البيانات).

3. الاختبار الآلي للهجرة (Automated Migration Testing):
   - يجب عدم الوثوق بالـ SQL المكتوب يدوياً! نستخدم `MigrationTestHelper` في اختبارات الـ Instrumentation لاختبار الترقية من الإصدار 1 إلى الإصدار N باستخدام ملفات الـ Schema JSON الحقيقية والتأكد من بقاء البيانات سليمة.

## Practical walkthrough

كتابة Migration يدوي واختباره والتأكد من سلامة البيانات في Room:
```kotlin
// 1. تعريف الـ Migration اليدوي من الإصدار 1 إلى 2:
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(db: SupportSQLiteDatabase) {
        // إضافة عمود جديد مع قيمة افتراضية صريحة لمنع الـ NULL values
        db.execSQL("ALTER TABLE users ADD COLUMN loyalty_points INTEGER NOT NULL DEFAULT 0")
        // إنشاء فهرس جديد لتسريع الاستعلامات
        db.execSQL("CREATE INDEX IF NOT EXISTS index_users_loyalty_points ON users(loyalty_points)")
    }
}

// 2. ربط الـ Migration في Database Builder:
@Database(entities = [UserEntity::class], version = 2, exportSchema = true)
abstract class AppDatabase : RoomDatabase() {
    companion object {
        fun buildDatabase(context: Context): AppDatabase {
            return Room.databaseBuilder(context, AppDatabase::class.java, "app_data.db")
                .addMigrations(MIGRATION_1_2)
                // ❌ ممنوع تماماً في الإنتاج:
                // .fallbackToDestructiveMigration()
                .build()
        }
    }
}
```

## Why it matters and how it works

Room validates schema and migration paths, but semantic correctness needs row-level tests. Backend must support old clients for a defined window, or return a controlled upgrade requirement. For encrypted files, key/backup migration requires separate recovery. A staged rollout should monitor migration crash rate by source version.

## Worked example

Conceptual compatibility matrix; CI should populate it from shipped variants.

```kotlin
data class CompatibilityCase(
    val oldDbVersion: Int,
    val newDbVersion: Int,
    val oldApiContract: Int,
    val expectedRows: Int,
)
// CI upgrades a real old schema fixture and asserts data + API behavior.
```

## Trade-offs and decision criteria

Additive backend fields ease old-app compatibility but prolong server complexity. Forced upgrades simplify backend but harm offline users and require product policy. Large local migrations can delay startup; plan chunking/recovery where necessary.

## Failure modes

A rename deployed to server before old clients adapt can break them. A destructive Room fallback may wipe drafts. A migration tested only from immediately prior version misses long-offline users. Rolling back APK after one-way DB upgrade can fail.

## Production perspective

A healthcare app tests every supported DB version with encrypted and plaintext fixtures, deploys backward-compatible API first, then stages new client and monitors migration failures. Contract removal occurs only after old-client usage falls below agreed threshold.

## Interview answer — short

Manage Room database migrations using explicit Migration classes or AutoMigrations, export schemas to JSON for version tracking, strictly avoid destructive fallbacks in production, and write automated instrumentation tests with MigrationTestHelper to verify schema upgrades against real databases.

## Interview answer — structured

Database migrations represent a high-stakes failure vector in mobile apps, as failed schema transitions crash the app upon startup.

First, **Never Use Destructive Fallbacks in Production**. Next, `fallbackToDestructiveMigration()` drops and recreates the SQLite database when a migration path is missing. This completely wipes offline user data, outbox queues, and cached credentials. It must be disabled in production releases.
**Explicit Migration Architecture**. For straightforward changes (adding new tables or nullable columns), leverage Room's `@AutoMigration` with `exportSchema = true`.
For non-trivial schema changes (renaming columns, changing primary keys, table splitting), write manual `Migration(from, to)` objects using explicit SQLite DDL statements. **Handling SQLite Limitations**.
SQLite versions prior to 3.35.0 do not support `ALTER TABLE DROP COLUMN`. Complex migrations require creating a temporary table, copying data, dropping the old table, and renaming the temporary table. **Automated Migration Testing**.
Finally, use Room's `MigrationTestHelper` in Android instrumented tests. The test runner boots SQLite with the v1 schema JSON, inserts sample fixtures, executes the migration to v2, and validates that all records remain intact and match the new schema hash.


## Interview answer — deep senior

From a data resilience perspective, senior architects prepare for edge cases in database lifecycle and multi-version jumps.

First, with Handling Multi-Version Hops (1 -> 5), users do not update their apps on every release. A user jumping from version 1 directly to version 5 must traverse the migration chain (`1->2`, `2->3`, `3->4`, `4->5`). Room chains matching migrations automatically. Ensure every sequential migration path exists and is covered by automated integration test matrices. Next, with Transaction Atomicity, Room executes migration blocks inside a single SQLite transaction. If an error occurs midway, SQLite rolls back changes to prevent partial or corrupted database states. Ensure manual migrations do not attempt non-transactional SQLite operations.
Finally, with Data Repair & Corruption Fallback, if hardware flash corruption or unrecoverable disk faults corrupt the database file, catch `SQLiteDatabaseCorruptException`. Rather than crashing permanently in an infinite loop, gracefully back up corrupted remnants to a diagnostics dump, re-initialize the database cleanly, and trigger a fresh background synchronization from the server.


## How to answer in the interview

- **Why:** users skip releases and backend deploys faster than apps.
- **How:** test old schema fixtures and stage additive API contracts before removal.
- **Trade-off:** compatibility windows increase temporary code and storage cost.
- **Failure case:** destructive migration deletes pending offline operations.
- **Production solution:** migration matrix, rollback plan, and adoption-based deprecation.

## Deep-dive talking points

Draw expand/migrate/contract sequence and old-app/new-server matrix.

## Follow-up questions

- **Interviewer:** "What does exportSchema = true do in Room?"
  **Answer:** "It exports the full database schema definition as a versioned JSON file at compile time, essential for Room to validate AutoMigrations and MigrationTestHelper."

- **Interviewer:** "Can Room handle migrations across non-consecutive versions?"
  **Answer:** "Yes, either by chaining consecutive migrations (1->2->3) or by providing a custom shortcut migration directly from 1->3."

## Self-check rubric

Can I test old databases, support old APKs and explain rollback limits?

## References and reviewed-on date

- [Android Room migrations](https://developer.android.com/training/data-storage/room/migrating-db-versions) — schema testing.
- [Android architecture guide](https://developer.android.com/topic/architecture) — persistent models.

Technically reviewed against primary documentation on 2026-10-13.
