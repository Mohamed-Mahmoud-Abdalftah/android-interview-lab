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

## Concept and technical explanation

Designing production Room database migrations requires evolving SQLite schemas incrementally without corrupting or dropping user data:
- Versioning & Schema Contracts: Every database modification requires incrementing the database version number in the @Database annotation and providing an explicit Migration(startVersion, endVersion) implementation containing raw SQL Data Definition Language (DDL) statements.
- SQLite Alter Table Limitations: SQLite has historically lacked support for dropping columns, altering column types, or modifying constraints in place. Complex migrations require a four-step table recreation pattern:
  1. Create a new temporary table with the desired schema, constraints, and defaults.
  2. Copy data from the old table into the temporary table using INSERT INTO ... SELECT.
  3. Drop the old table via DROP TABLE.
  4. Rename the temporary table to the original table name via ALTER TABLE ... RENAME TO.
- Testing & Verification:
  * Export Schema: Configure room.schemaLocation in Gradle so KSP exports a JSON snapshot of each database version schema into Git version control.
  * Automated Migration Tests: Use Room's MigrationTestHelper in instrumented tests to create an old database version, populate it with mock user records, execute the migration, and assert that data remains uncorrupted and tables match the exported schema.
- The Golden Production Rule: Strictly forbid fallbackToDestructiveMigration() in release builds, as it drops all SQLite tables and wipes user data upon schema mismatches.

## Practical walkthrough (English)

Comprehensive Room migration with table recreation and automated test:
```kotlin
// 1. Defining a complex migration that splits columns and adds foreign keys
val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(db: SupportSQLiteDatabase) {
        // Step 1: Create temp table with updated schema
        db.execSQL(
            "CREATE TABLE users_temp (" +
            "id TEXT PRIMARY KEY NOT NULL, " +
            "firstName TEXT NOT NULL, " +
            "lastName TEXT NOT NULL, " +
            "email TEXT NOT NULL DEFAULT '')"
        )

        // Step 2: Copy existing data over
        db.execSQL(
            "INSERT INTO users_temp (id, firstName, lastName) " +
            "SELECT id, firstName, lastName FROM users"
        )

        // Step 3: Drop old table
        db.execSQL("DROP TABLE users")

        // Step 4: Rename temp table to final name
        db.execSQL("ALTER TABLE users_temp RENAME TO users")

        // Step 5: Recreate indices
        db.execSQL("CREATE UNIQUE INDEX IF NOT EXISTS index_users_email ON users(email)")
    }
}

// 2. Automated Migration Test using MigrationTestHelper
@RunWith(AndroidJUnit4::class)
class DatabaseMigrationTest {
    @get:Rule
    val helper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java.canonicalName,
        FrameworkSQLiteOpenHelperFactory()
    )

    @Test
    fun migrate2To3_preservesUserData() {
        // Create DB at version 2 and insert test record
        helper.createDatabase("test-db", 2).apply {
            execSQL("INSERT INTO users (id, firstName, lastName) VALUES ('u1', 'Mohamed', 'Mahmoud')")
            close()
        }

        // Run migration to version 3 and validate constraints
        val db = helper.runMigrationsAndValidate("test-db", 3, true, MIGRATION_2_3)
        val cursor = db.query("SELECT id, firstName, lastName, email FROM users WHERE id = 'u1'")
        cursor.moveToFirst()
        assertEquals("Mohamed", cursor.getString(1))
        assertEquals("", cursor.getString(3)) // Default value populated
        cursor.close()
    }
}
```

## Explanation in Arabic

كيف تصمم ترحيل قاعدة بيانات Room (Database Migration) يحافظ على بيانات المستخدم بنسبة 100% دون فقدان أي بيانات؟

1. خطورة ترقية الـ Database في الإنتاج:
   - عندما تعدل أي `@Entity` (إضافة عمود، حذف عمود، تغيير نوع بيانات)، يجب زيادة رقم `version` في `@Database`.
   - إذا قمت بزيادة الرقم دون كتابة `Migration`، سينهار التطبيق فوراً عند فتحه لدى المستخدم مع خطأ: `IllegalStateException: Room cannot verify the data integrity!`.
   - **الكارثة الكبرى**: استخدام `fallbackToDestructiveMigration()`! هذا الإعداد يحذف قاعدة البيانات بالكامل ويعيد بناءها فارغة، مما يمسح مسودات المستخدم وعملياته غير المتصلة بالإنترنت!

2. خطوات تصميم ترحيل آمن واحترافي:
   - **تفعيل Schema Export في Gradle**: إعداد `room.schemaLocation` لحفظ ملفات الـ JSON لكل إصدار في Git.
   - **كتابة كود الـ Migration الصريح**: استخدام أوامر SQLite القياسية (`ALTER TABLE ... ADD COLUMN ...`).
   - **التعامل مع تعديل الأعمدة المعقد**: SQLite لا يدعم تعديل نوع عمود مباشرة. الخطوات القياسية: إنشاء جدول مؤقت بالهيكل الجديد، نسخ البيانات من الجدول القديم، حذف الجدول القديم، وإعادة تسمية الجدول المؤقت.
   - **كتابة MigrationTest آلي**: اختبار الـ Migration باستخدام `MigrationTestHelper` قبل إطلاق التطبيق.

## Practical walkthrough

كتابة كود Migration دقيق مع اختبار آلي للتأكد من سلامة البيانات:
```kotlin
// 1. تعريف مسار الترحيل من الإصدار 1 إلى الإصدار 2:
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(db: SupportSQLiteDatabase) {
        // إضافة عمود جديد مع قيمة افتراضية لتفادي NULL في الأعمدة الإلزامية:
        db.execSQL("ALTER TABLE orders ADD COLUMN tracking_number TEXT DEFAULT NULL")
    }
}

// 2. ترحيل معقد: تغيير عمود أو حذف عمود (تتطلب إنشاء جدول جديد):
val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(db: SupportSQLiteDatabase) {
        // أ. إنشاء جدول جديد بالهيكل المطلوب:
        db.execSQL("""
            CREATE TABLE orders_new (
                id TEXT PRIMARY KEY NOT NULL,
                amount_cents INTEGER NOT NULL,
                tracking_number TEXT
            )
        """.trimIndent())
        // ب. نسخ البيانات من القديم للجديد:
        db.execSQL("INSERT INTO orders_new (id, amount_cents, tracking_number) SELECT id, amount_cents, tracking_number FROM orders")
        // ج. حذف القديم وإعادة التسمية:
        db.execSQL("DROP TABLE orders")
        db.execSQL("ALTER TABLE orders_new RENAME TO orders")
    }
}

// 3. اختبار الترحيل الآلي عبر MigrationTestHelper:
@Test
fun testMigration1To2PreservesData() {
    // إنشاء DB بالإصدار 1 وكتابة بيانات حقيقية:
    helper.createDatabase(TEST_DB, 1).apply {
        execSQL("INSERT INTO orders (id, amount_cents) VALUES ('ord_1', 5000)")
        close()
    }
    // تشغيل الترحيل للإصدار 2 والتحقق من بقاء البيانات:
    val db = helper.runMigrationsAndValidate(TEST_DB, 2, true, MIGRATION_1_2)
    val cursor = db.query("SELECT * FROM orders WHERE id = 'ord_1'")
    assertTrue(cursor.moveToFirst())
    assertEquals(5000L, cursor.getLong(cursor.getColumnIndexOrThrow("amount_cents")))
}
```

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

Designing a data-preserving Room migration requires incrementing database version numbers, providing explicit SQL DDL migrations, and utilizing the 4-step table recreation pattern for complex alterations. Schema JSON dumps and MigrationTestHelper automate validation in CI, while destructive fallback migrations are strictly banned in release builds.

## Interview answer — structured

Designing safe database migrations in Android requires a disciplined approach to schema evolution and automated testing.
First, every schema change requires bumping the Room database version and supplying a custom Migration object. For simple changes like adding a nullable column, a raw ALTER TABLE ADD COLUMN statement suffices.
Second, because SQLite does not permit direct column deletions or constraint modifications, complex schema shifts require a 4-step migration: creating a temporary table with the target schema, copying existing user records via INSERT INTO SELECT, dropping the old table, and renaming the temporary table.
Third, migrations must be verified automatically before production release. By enabling schema exports in Gradle, we write instrumented tests using MigrationTestHelper to simulate real upgrades and confirm zero data loss, strictly banning fallbackToDestructiveMigration in production.

## Interview answer — deep senior

In production applications storing offline-first user state, a failed database migration is an existential threat that leads to immediate app crashes on launch or catastrophic data loss.
The most frequent production bug occurs when an engineer relies on fallbackToDestructiveMigration().
While convenient during early prototyping, shipping this flag to production guarantees that whenever the database version increases, Room silently wipes all SQLite tables, erasing unsynced user drafts, cached credentials, and offline purchase records.
To evolve schemas safely, we enforce a strict migration protocol.
Because SQLite lacks full ALTER TABLE capabilities, removing a column or adding a NOT NULL constraint without a default requires the classic temporary table shuffle: creating the new table structure, copying over data with fallback defaults, dropping the legacy table, and renaming the temporary table.
To guarantee mathematical correctness, we export Room schemas as JSON artifacts tracked in Git version control via the room.schemaLocation Gradle compiler argument.
In our CI pipeline, an automated test suite powered by MigrationTestHelper executes every historical migration path against real SQLite instances, seeding mock customer records into version N and asserting their integrity in version N+1.
This end-to-end automated verification guarantees that millions of existing users upgrade smoothly without a single lost record or launch crash.

## How to answer in the interview

- **Why:** A schema upgrade is a user-data preservation operation.
- **How:** Inventory shipped versions, export schemas, backfill and test full paths.
- **Trade-offs:** Use auto migration only for transformations it expresses safely.
- **Failure cases:** Wrong default, missing upgrade path, destructive fallback.
- **Production solution:** Representative old DB fixtures, invariant checks and staged rollout.

## Deep-dive talking points

Cover old-version matrix, row-level assertions, storage failure and staged rollback limits.

## Follow-up questions

- **Interviewer:** "What is `AutoMigration` in Room?"
  **Answer:** "Introduced in Room 2.4, `@AutoMigration` generates simple migrations (adding columns, creating tables) automatically using exported schema JSON diffs."

- **Interviewer:** "What happens if a NOT NULL column is added without a DEFAULT value during migration?"
  **Answer:** "SQLite throws an error during migration because existing rows would have NULL in a NOT NULL column; always supply a default value."

## Self-check rubric

Can I enumerate shipped versions, protect rows, reject destructive fallback and test low-storage failure?

## References and reviewed-on date

- [Android Room migrations](https://developer.android.com/training/data-storage/room/migrating-db-versions) — migration and testing guidance.

Technically reviewed against primary documentation on 2026-10-13.
