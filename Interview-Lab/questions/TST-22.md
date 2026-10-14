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

Generate realistic fixtures by creating pre-migration v1 SQLite databases populated with dirty legacy data: null values in deprecated columns, Unicode/emoji strings, and orphaned keys. Test using MigrationTestHelper to ensure ALTER TABLE and copy queries handle edge cases without SQLiteConstraintExceptions.

## Interview answer — structured

Database migrations frequently pass clean unit tests but crash on real devices due to historical dirty data accumulated across years of app usage.

First, **Production Dirty Data Realities**. Next, adding a `NOT NULL` column to an existing table without an explicit `DEFAULT` value fails when legacy rows exist.
Historical rows with `NULL` or empty strings in fields previously unconstrained. Broken foreign keys (orphaned rows) resulting from unconstrained deletes in legacy app versions.
Non-standard UTF-8 strings (emojis, RTL Arabic scripts, zero-width spaces). **Constructing Realistic Test Fixtures**.
Use `helper.createDatabase(DB_NAME, oldVersion)` to boot the historical schema. Populate the table with adversarial edge-case fixtures: `NULL` entries, 50,000 dummy rows to test SQLite transaction memory limits, malformed timestamps, and corrupted foreign key IDs.
**Hardening Migration Logic**. Finally, update manual SQL migrations to scrub or sanitize dirty data inline: execute `UPDATE customers SET email = 'unknown' WHERE email IS NULL` before executing the `ALTER TABLE` statement or table-copy routine.


## Interview answer — deep senior

From an operational data integrity perspective, preventing migration crashes requires defensive SQL design.

First, with Table Recreation Pattern for Complex Migrations, SQLite versions prior to 3.35.0 do not support dropping columns. Complex migrations require: (1) creating `new_table`, (2) copying sanitized rows with `INSERT OR IGNORE INTO new_table SELECT ... FROM old_table`, (3) dropping `old_table`, and (4) renaming `new_table` to `old_table`. Test this exact 4-step sequence against dirty fixtures. Next, with Sanitized Production Snapshot Testing, for high-risk financial migrations, export an anonymized SQLite dump from an internal test account that has existed through 5 years of production upgrades. Load this real SQLite binary directly into an instrumented migration test fixture in CI.
Finally, with Transaction Rollback Safety, verify that if a migration statement fails mid-script, the entire migration aborts atomically without leaving the database in an unrecoverable mixed-version schema state.


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
