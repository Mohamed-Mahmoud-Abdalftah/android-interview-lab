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

## Concept and technical explanation

Testing SQLite database migrations against legacy customer data requires generating production-realistic, privacy-compliant test fixtures to validate complex schema transformations before release. Database migrations frequently succeed against empty schemas but crash catastrophically in production when encountering historical edge cases: unexpected NULL values in columns subsequently designated NOT NULL, legacy un-normalized text encodings, violated foreign key constraints, or partial migrations from long-discontinued app versions. Android's official Room testing artifact provides MigrationTestHelper to mechanically construct databases at historical schema versions, execute real DDL/DML migration scripts, and validate schema integrity. To produce realistic data without violating privacy regulations (GDPR/HIPAA), engineering teams never copy raw production database dumps. Instead, they synthesize realistic fixtures using schema-aware generators that model legacy data distributions, corrupted edge cases, and extreme schema variants.

## Practical walkthrough (English)

Creating historical schema fixtures and testing Room database migrations with MigrationTestHelper:
```kotlin
@RunWith(AndroidJUnit4::class)
class CustomerDatabaseMigrationTest {
    private val TEST_DB = "migration-test.db"

    @get:Rule
    val helper: MigrationTestHelper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java.canonicalName,
        FrameworkSQLiteOpenHelperFactory()
    )

    @Test
    fun migrateV1ToV2_legacyCorruptedCustomerData_migratesSuccessfully() {
        // 1. Create database at historical Version 1 using auto-generated schema JSON
        var db = helper.createDatabase(TEST_DB, 1).apply {
            // 2. Insert realistic legacy customer fixtures directly via raw SQLite
            execSQL("INSERT INTO customers (id, name, legacy_notes, phone) VALUES ('cust_101', 'O''Connor & Sons', 'Legacy customer imported in 2018', NULL)")
            execSQL("INSERT INTO customers (id, name, legacy_notes, phone) VALUES ('cust_102', 'Global Logistics Ltd', NULL, '+1-555-0199')")
            close()
        }

        // 3. Execute Migration 1 -> 2 and validate schema integrity automatically
        db = helper.runMigrationsAndValidate(TEST_DB, 2, true, MIGRATION_1_2)

        // 4. Assert that legacy data was transformed safely according to new schema rules
        val cursor = db.query("SELECT id, name, phone, status FROM customers WHERE id = 'cust_101'")
        assertTrue(cursor.moveToFirst())

        // Verify NOT NULL default constraint applied safely to legacy NULL field
        val phoneIndex = cursor.getColumnIndex("phone")
        val statusIndex = cursor.getColumnIndex("status")
        assertEquals("UNSPECIFIED", cursor.getString(phoneIndex))
        assertEquals("ACTIVE", cursor.getString(statusIndex))
        cursor.close()
    }
}
```

## Explanation in Arabic

ترقية قاعدة بيانات (Room Migration) تفشل فقط عند تطبيقها على بيانات حقيقية لعملاء قدامى في الإنتاج. كيف تنشئ عينات اختبار واقعية (Realistic Fixtures) لحل المشكلة؟

1. لماذا تفشل الترقيات على بيانات الإنتاج وتنجح في الاختبارات البسيطة؟
   - في الاختبارات الأولية، يختبر المطور بيانات مثالية ونظيفة (`User("1", "Ahmed")`).
   - في بيانات الإنتاج الواقعية لآلاف العملاء القدامى، توجد حالات شاذة:
     * حقول قديمة تحتوي على قيم `NULL` بينما يفرض الـ Migration الجديد `NOT NULL` بدون قيمة افتراضية!
     * نصوص تحتوي على Emojis ورموز غير قياسية (Unicode Characters).
     * سجلات تالفة أو مفاتيح خارجية مفقودة (Orphaned Foreign Keys) بسبب انهيارات قديمة.
     * جداول ضخمة تحتوي على ملايين السجلات تستهلك الذاكرة وتتجاوز مهلة الـ SQLite Transaction.

2. كيفية إنشاء Realistic Test Fixtures حتمية:
   - **أخذ نسخة مشفرة ومطهرة (Anonymized & Sanitized DB Dump)**: استخراج عينة من قاعدة بيانات إنتاج قديمة، وتطهيرها من جميع البيانات الحساسة (PII) لاستخدامها كملف اختبار.
   - **إنشاء سكريبت ملء بيانات شاذة (Dirty Data Populator)**: إدخال بيانات تحتوي على نصوص فارغة، رموز صينية، أرقام سالبة، وقيم قصوى في جدول الـ v1 قبل بدء الـ Migration.
   - **فحص استثناء `SQLiteConstraintException`** وإصلاح الـ SQL بإضافة `DEFAULT` values أو تنظيف السجلات التالفة داخل الـ Migration نفسه.

## Practical walkthrough

إنشاء عينة بيانات إنتاج معقدة وشاذة واختبار هجرة Room المخصصة عليها:
```kotlin
@RunWith(AndroidJUnit4::class)
class RealisticCustomerMigrationTest {
    @get:Rule
    val helper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java
    )

    @Test
    fun migration2To3_handlesDirtyCustomerDataGracefully() {
        val dbV2 = helper.createDatabase("dirty-data-test.db", 2).apply {
            // 1. إدخال بيانات غير مثالية ومطابقة لحالات الإنتاج الواقعية:
            execSQL("INSERT INTO customers (id, name, legacy_email) VALUES ('c1', 'Ali 😊', NULL)") // Legacy email is NULL!
            execSQL("INSERT INTO customers (id, name, legacy_email) VALUES ('c2', '', 'user@test.com')") // Empty name!
            close()
        }

        // 2. تنفيذ الـ Migration الذي يضيف عمود NOT NULL:
        // إذا لم يكن كود الـ Migration يحتوي على DEFAULT value صريح، سيفشل هذا السطر برمي SQLiteConstraintException!
        val dbV3 = helper.runMigrationsAndValidate("dirty-data-test.db", 3, true, MIGRATION_2_3)

        // 3. التحقق من بقاء بيانات العميل c1 دون انهيار واستبدال الـ NULL بقيمة آمنة:
        val cursor = dbV3.query("SELECT id, name, standardized_email FROM customers WHERE id = 'c1'")
        assertTrue(cursor.moveToFirst())
        assertEquals("Ali 😊", cursor.getString(1))
        assertEquals("no-email@domain.com", cursor.getString(2))
    }
}
```

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

We test legacy migrations using Room's MigrationTestHelper, which boots historical schemas from versioned JSON files. We never copy raw user data due to privacy laws. Instead, we generate synthetic fixtures reflecting real customer anomalies: unexpected nulls, unescaped quotes, missing foreign keys, and empty strings. We insert these into the historical database, run the migration, and assert that data transformed cleanly without data loss or crashes.

## Interview answer — structured

Database migrations represent the highest-risk release boundary because a migration crash triggers fatal SQLiteException crashes on app startup, leaving users locked out until they reinstall.
A common engineering blind spot is testing migrations against clean, newly created tables rather than realistic legacy data.
In production, databases that have survived years of updates contain subtle anomalies: NULL entries created before a column became required, non-standard text encodings, and orphan rows left by unconstrained deletions.
To validate migrations thoroughly, we leverage Room's MigrationTestHelper.
This tool reads historical schema contracts exported as JSON files in app/schemas, constructing an authentic SQLite database matching the exact structural layout of older releases.
Because privacy compliance (GDPR and HIPAA) strictly forbids copying production databases into test environments, we synthesize realistic fixtures.
We author fixture generators that populate historical schemas with realistic edge-case distributions: strings containing SQL special characters like single quotes, corrupted timestamps, and default fallbacks for newly mandated non-null columns.
We execute helper.runMigrationsAndValidate, asserting that SQLite indexes, foreign keys, and migrated values conform to the target version without data loss.

## Interview answer — deep senior

Under the hood, Room's MigrationTestHelper coordinates SQLite master tables, JSON schema specifications, and SQLite PRAGMA table information inspection.
During the Gradle build, Room's annotation processor generates schema definitions in app/schemas/<database_class>/<version>.json, describing exact SQLite CREATE TABLE, CREATE INDEX, and table hash identities.
When helper.createDatabase(name, version) runs, the test helper interprets the JSON schema, executing low-level SQLite DDL statements on the underlying FrameworkSQLiteOpenHelper to rebuild the ancient schema.
We then execute raw SQLite INSERT queries to inject our synthetic legacy fixtures.
These fixtures intentionally stress common SQLite failure vectors: inserting NULL into columns that the upcoming migration will alter to NOT NULL with an ALTER TABLE command (which SQLite natively restricts without table re-creation), inserting non-ASCII Unicode glyphs, and creating broken foreign key relationships.
When helper.runMigrationsAndValidate is invoked, Room executes the defined Migration scripts, then queries SQLite's internal pragma table_info(tableName) and pragma index_list(tableName) to perform a field-by-field, type-affinity, and nullability comparison against the target schema JSON.
If a column affinity or nullability contract does not match with 100% precision, Room throws an IllegalStateException before production release.
Senior engineers automate matrix migration testing, verifying direct jumps from version 1 to 5 alongside incremental hops from 1 to 2, 2 to 3, and so on.

## How to answer in the interview

- **Why:** synthetic clean rows miss legacy data hazards.
- **How:** seed null, duplicate and Unicode cases for each supported schema path.
- **Trade-off:** more fixtures take maintenance but protect real migrations.
- **Failure case:** unique index fails or picks the wrong canonical row.
- **Production solution:** deterministic merge rule and staged rollout monitoring.

## Deep-dive talking points

Prompt for exported schemas, production shape not raw PII, duplicate resolution, all upgrade paths and performance.

## Follow-up questions

- **Interviewer:** "Why does adding a NOT NULL column without a DEFAULT fail in SQLite?"
  **Answer:** "Because SQLite cannot populate existing historical rows for the new column, triggering an immediate SQLiteConstraintException: Cannot add a NOT NULL column with default value NULL."

- **Interviewer:** "What is the 12-step table recreation procedure in SQLite?"
  **Answer:** "The official SQLite pattern for modifying existing table structures (such as changing column constraints or types) by copying data into a newly created schema and dropping the old table."

## Self-check rubric

Seed every supported old schema with duplicate, null, Arabic/Unicode and long-text cases. Define the merge policy before migration and assert canonical rows, counts and foreign keys after each upgrade path.

## References and reviewed-on date

- [Room migration testing](https://developer.android.com/training/data-storage/room/migrating-db-versions) — exported schemas and helper.
- [Room migration overview](https://developer.android.com/training/data-storage/room/migrating-db-versions) — migration paths.

Technically reviewed against primary documentation on 2026-10-13.
