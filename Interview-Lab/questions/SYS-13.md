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

## Concept and technical explanation

Managing local database schema evolution across millions of active Android devices is one of the highest-risk operations in mobile engineering. Unlike backend database migrations where operations run centrally in synchronized rollout windows, mobile app updates are completely asynchronous. Users may skip multiple app releases, jumping directly from an ancient database version to the newest release. In Room, failing to handle migrations properly triggers an IllegalStateException that crashes the application on cold startup. Destructive migrations must be strictly forbidden in production. Schema evolution requires writing deterministic Migration objects with explicit raw SQLite DDL scripts. Furthermore, schema files must be exported via room.schemaLocation and validated in automated continuous integration using MigrationTestHelper. Backwards compatibility must also extend to the remote backend, ensuring that database entities accommodate nullable columns, default values, and schema rollbacks during staged Play Store rollouts.

## Practical walkthrough (English)

Implementing deterministic Room migrations with automated validation tests:
```kotlin
// 1. Explicit incremental database migrations with safe DDL modifications
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(db: SupportSQLiteDatabase) {
        // Adding a column with a strict NOT NULL constraint and default fallback
        db.execSQL("ALTER TABLE orders ADD COLUMN delivery_notes TEXT NOT NULL DEFAULT ''")
        // Creating an index to support fast queried lookups
        db.execSQL("CREATE INDEX IF NOT EXISTS index_orders_created_at ON orders(created_at)")
    }
}

val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(db: SupportSQLiteDatabase) {
        // SQLite does not support dropping columns directly in older engines; recreate table safely
        db.execSQL(
            "CREATE TABLE orders_new (" +
            "id TEXT PRIMARY KEY NOT NULL, " +
            "total_cents INTEGER NOT NULL, " +
            "delivery_notes TEXT NOT NULL, " +
            "created_at INTEGER NOT NULL)"
        )
        db.execSQL("INSERT INTO orders_new (id, total_cents, delivery_notes, created_at) SELECT id, total_cents, delivery_notes, created_at FROM orders")
        db.execSQL("DROP TABLE orders")
        db.execSQL("ALTER TABLE orders_new RENAME TO orders")
    }
}

// 2. Automated MigrationTestHelper verifying schema integrity across update jumps
@RunWith(AndroidJUnit4::class)
class OrderDatabaseMigrationTest {
    private val TEST_DB = "migration-test"

    @get:Rule
    val helper: MigrationTestHelper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java
    )

    @Test
    fun migrate1To3_containsValidData() {
        // Create database with version 1 and insert seed data
        var db = helper.createDatabase(TEST_DB, 1).apply {
            execSQL("INSERT INTO orders (id, total_cents, created_at) VALUES ('ord_101', 5000, 1600000000)")
            close()
        }

        // Run migrations across both versions and validate final schema
        db = helper.runMigrationsAndValidate(TEST_DB, 3, true, MIGRATION_1_2, MIGRATION_2_3)
        val cursor = db.query("SELECT delivery_notes FROM orders WHERE id = 'ord_101'")
        assertTrue(cursor.moveToFirst())
        assertEquals("", cursor.getString(0))
        cursor.close()
    }
}
```

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

We manage Room database evolution by writing explicit migration scripts with raw SQLite DDL and testing them automatically using MigrationTestHelper. We ban destructive fallbacks in production, add new columns with safe default values, and support multi-version upgrade paths for users who skip intermediate application releases.

## Interview answer — structured

Managing database migrations in Android requires safeguarding user offline data while accommodating asynchronous client update cycles.
I prohibit fallbackToDestructiveMigration in production builds because wiping local databases destroys pending offline mutations and cached credentials.
Every schema change requires an explicit Room Migration object executing raw SQLite commands. When adding new columns, we define non-null constraints with safe default values to preserve existing records.
Because Android users often skip multiple app versions, Room chains individual migration paths automatically, such as executing migration one to two followed immediately by two to three.
We export JSON schema snapshots via the room.schemaLocation compiler argument.
In our continuous integration test suite, we implement automated migration tests using Room MigrationTestHelper, asserting that databases populated with legacy records successfully upgrade and maintain data integrity across version jumps.

## Interview answer — deep senior

From a staff database engineering perspective, mobile schema migrations require deep knowledge of SQLite internal limitations and backend synchronization lifecycles.
Older SQLite engines embedded in Android lack support for standard DDL operations like dropping columns or altering constraints. In these scenarios, the migration must execute a classic table recreation sequence: create a temporary table with the new schema, copy existing data from the legacy table, drop the legacy table, and rename the new table. This sequence must execute within an atomic transaction to prevent corrupt half-migrated states if the app process crashes mid-flight.
When deploying staged rollouts on the Play Store, schema changes must maintain backwards compatibility with both older app clients and backend APIs. If an update introduces a new entity attribute, the local database and backend contracts must treat that attribute as optional during the rollout window. If a catastrophic bug forces an app rollback, older binaries must still function without crashing over unrecognised server fields.
For massive enterprise tables containing hundreds of thousands of records, running synchronous migrations on the main thread during app cold launch causes severe ANRs. For non-critical analytics or cache tables, we execute asynchronous background migrations, presenting a lightweight splash screen or deferring non-essential table upgrades until after interactive UI initialization.
Finally, we implement a defensive corrupted database recovery hook. If SQLite encounters physical flash corruption, rather than crashing in an infinite bootloop, the framework captures the error, attempts database vacuum recovery, and safely re-initializes clean state as a last resort.

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
