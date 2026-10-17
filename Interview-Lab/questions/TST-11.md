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

## Concept and technical explanation

Testing local persistence with Room requires isolating database operations into three specialized verification tiers: DAO contract testing, database migration testing, and transactional rollback testing. DAO unit testing validates CRUD queries, relational joins, transactions, and reactive Flow emissions using an ephemeral in-memory database built via Room.inMemoryDatabaseBuilder(). Database migration testing is mission-critical and must be executed as an instrumentation test using Room's MigrationTestHelper; it programmatically creates the database at historical schema version N, populates it with realistic raw SQLite fixtures, executes the Migration(N, N+1) object, and asserts that the schema hash and persisted data survive intact without data loss. Transaction testing verifies that multi-table batch operations roll back atomically when any constituent operation throws an exception, preventing database corruption.

## Practical walkthrough (English)

Testing Room DAOs in memory and verifying database schema migrations using MigrationTestHelper:
```kotlin
// 1. In-Memory DAO Testing on JVM / Instrumentation
@RunWith(AndroidJUnit4::class)
class UserDaoTest {
    private lateinit var db: AppDatabase
    private lateinit var userDao: UserDao

    @Before
    fun createDb() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        db = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java)
            .allowMainThreadQueries() // Acceptable strictly in isolated unit tests
            .build()
        userDao = db.userDao()
    }

    @After
    fun closeDb() = db.close()

    @Test
    fun insertAndReadUser() = runTest {
        val user = UserEntity(id = 1, name = "Mahmoud")
        userDao.insert(user)
        assertEquals("Mahmoud", userDao.findById(1)?.name)
    }
}

// 2. Migration Instrumentation Test using MigrationTestHelper
@RunWith(AndroidJUnit4::class)
class AppDatabaseMigrationTest {
    private val TEST_DB = "migration-test.db"

    @get:Rule
    val helper: MigrationTestHelper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java.canonicalName,
        FrameworkSQLiteOpenHelperFactory()
    )

    @Test
    fun migrate1To2_addsEmailColumn_andPreservesData() {
        // Create DB at version 1 and insert legacy row via raw SQLite
        helper.createDatabase(TEST_DB, 1).apply {
            execSQL("INSERT INTO users (id, name) VALUES (1, 'Ali')")
            close()
        }

        // Re-open and run migration to version 2 (adds email column)
        val db = helper.runMigrationsAndValidate(TEST_DB, 2, true, MIGRATION_1_2)

        // Verify data survived and new column defaults properly
        val cursor = db.query("SELECT id, name, email FROM users WHERE id = 1")
        assertTrue(cursor.moveToFirst())
        assertEquals("Ali", cursor.getString(cursor.getColumnIndexOrThrow("name")))
        assertEquals("", cursor.getString(cursor.getColumnIndexOrThrow("email")))
        cursor.close()
    }
}
```

## Explanation in Arabic

كيف تختبر دوال الـ Room DAOs، وترقيات قاعدة البيانات (Database Migrations)، والمعاملات الذرية (Transactions) بشكل معزول؟

1. اختبار الـ Room DAOs (In-Memory Database):
   - نستخدم `Room.inMemoryDatabaseBuilder()` في مجلد `src/test/` (مع Robolectric) أو `src/androidTest/` (على محاكي حقيقي).
   - ميزة قاعدة البيانات في الذاكرة: سرعة فائقة، وتبدأ فارغة تماماً مع كل اختبار، وتُحذف فور إغلاقها (`db.close()`) دون ترك أي ملفات ملوثة على القرص.
   - تفعيل `allowMainThreadQueries()` لتسهيل كتابة الاختبارات المتزامنة.

2. اختبار ترقيات قاعدة البيانات (Room Migration Testing):
   - **قاعدة ذهبية**: لا تعتمد على التجربة اليدوية! استخدم أداة `MigrationTestHelper` الرسمية.
   - يقوم الاختبار بإنشاء قاعدة بيانات حقيقية بالإصدار 1 (باستخدام ملف الـ Schema JSON القديم)، وإدخال بيانات حقيقية، ثم تنفيذ الـ Migration إلى الإصدار 2، والتحقق من أن البيانات لم تُفقد وأن الجداول والأعمدة الجديدة مطابقة للـ Hash الجديد.

3. اختبار المعاملات الذرية (Transactions Testing):
   - التحقق من أنه إذا فشلت عملية كتابة في المنتصف، يتم التراجع عن جميع العمليات السابقة (Rollback) ولا تُترك قاعدة البيانات في حالة متناقضة.

## Practical walkthrough

اختبار DAO في الذاكرة واختبار هجرة Room باستخدام MigrationTestHelper:
```kotlin
// 1. اختبار Room DAO في الذاكرة (In-Memory Database Test):
@RunWith(AndroidJUnit4::class)
class UserDaoInMemoryTest {
    private lateinit var db: AppDatabase
    private lateinit var userDao: UserDao

    @Before
    fun createDb() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        db = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java)
            .allowMainThreadQueries()
            .build()
        userDao = db.userDao()
    }

    @Test
    fun insertUserAndReadInList() = runTest {
        val user = UserEntity(id = "usr_1", name = "Sarah")
        userDao.insert(user)
        val users = userDao.getAllUsers().first()
        assertEquals(1, users.size)
        assertEquals("Sarah", users[0].name)
    }

    @After
    fun closeDb() = db.close()
}

// 2. اختبار Migration حقيقي من الإصدار 1 إلى 2 عبر MigrationTestHelper:
@RunWith(AndroidJUnit4::class)
class DatabaseMigrationTest {
    private val TEST_DB = "migration-test.db"

    @get:Rule
    val helper: MigrationTestHelper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java
    )

    @Test
    fun migrate1To2_preservesExistingUserData() {
        // إنشاء قاعدة بيانات بالإصدار 1 وإدخال بيانات قديمة
        helper.createDatabase(TEST_DB, 1).apply {
            execSQL("INSERT INTO users (id, name) VALUES ('u1', 'Omar')")
            close()
        }

        // تشغيل الـ Migration إلى الإصدار 2 والتحقق من صحة الـ Schema
        val dbV2 = helper.runMigrationsAndValidate(TEST_DB, 2, true, MIGRATION_1_2)
        
        // التأكد من أن بيانات Omar ما زالت موجودة والعمود الجديد أخذ قيمته الافتراضية:
        val cursor = dbV2.query("SELECT id, name, loyalty_points FROM users WHERE id = 'u1'")
        assertTrue(cursor.moveToFirst())
        assertEquals("Omar", cursor.getString(1))
        assertEquals(0, cursor.getInt(2)) // القيمة الافتراضية المضافة في v2
    }
}
```

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

We test Room across three tiers. DAO queries and transactions are tested using an in-memory database built with Room.inMemoryDatabaseBuilder, ensuring fast, isolated execution that clears on close. Database migrations are verified on an emulator using MigrationTestHelper, which boots the database at version N, inserts legacy raw SQL fixtures, executes the Migration to N+1, and validates the schema hash and data integrity without data loss.

## Interview answer — structured

Securing enterprise persistence in Android requires an unyielding testing strategy across Room DAOs, schema migrations, and database transactions.
For DAO testing, we avoid touching disk storage by constructing an ephemeral in-memory database using Room.inMemoryDatabaseBuilder().
Because the database resides purely in RAM, tests execute rapidly and leave zero state behind upon teardown.
We test complex SQL queries, relational entity joins, cascading foreign key deletions, and reactive Flow emissions to verify that Room generates correct SQLite query plans.
For database migrations, testing is non-negotiable because an invalid migration crashes the application on app launch with an IllegalStateException in production.
We write automated instrumentation tests using Room's MigrationTestHelper.
The helper creates the database at historical version N using Room's exported schema JSON files, allows us to insert realistic legacy SQLite records, executes the production Migration(N, N+1) instance, and validates that the resulting schema matches version N+1 perfectly while preserving existing customer records.
Finally, we test multi-operation database transactions annotated with @Transaction, intentionally throwing an exception mid-operation to assert that Room rolls back all intermediate inserts atomically, preventing database corruption.

## Interview answer — deep senior

Under the hood, Room database testing relies on SQLite's in-memory VFS and Room's schema identity hash verification architecture.
When Room.inMemoryDatabaseBuilder is used, Room passes :memory: as the database filename to sqlite3_open_v2.
The operating system creates an anonymous, private in-memory database instance tied to the SQLite connection handle; closing the connection instantly returns the RAM pages to the OS without disk I/O bottlenecks.
For schema migrations, Room enforces compile-time schema safety through exported JSON files generated by room.schemaLocation in the Gradle build configuration.
Every schema version generates a JSON snapshot detailing table names, column affinities, nullability constraints, primary keys, and indices, alongside an identityHash string.
When MigrationTestHelper.runMigrationsAndValidate(name, targetVersion, validateDroppedTables, migration) executes, it inspects targetVersion's JSON schema file.
It executes the custom Migration SQL statements on the SQLite engine and subsequently queries sqlite_master to reconstruct the actual schema in memory.
It compares this runtime schema column-by-column against the expected schema JSON.
Finally, it updates the room_master_table with the new identityHash.
If an engineer accidentally made a column NOT NULL without a DEFAULT value in the migration SQL, or mismatched an index definition, the helper fails with an explicit IllegalStateException diff detailing the exact column discrepancy before production release.
Senior engineers automate migration tests across all historic upgrade paths (such as migrating directly from v1 to v5) in CI pipelines to guarantee zero-crash updates for legacy app users.

## How to answer in the interview

- **Why:** old customer data is where schema changes fail.
- **How:** create versioned fixtures, migrate and assert rows, indexes and rollback.
- **Trade-off:** in-memory speed versus file/device durability evidence.
- **Failure case:** schema validation passes while duplicate rows merge incorrectly.
- **Production solution:** release-like migration matrix from every supported version.

## Deep-dive talking points

Prompt for exported schemas, realistic old rows, all upgrade paths, rollback and remote boundary.

## Follow-up questions

- **Interviewer:** "Why is allowMainThreadQueries() safe in Room unit tests?"
  **Answer:** "Because test runners execute synchronously on single test threads; main thread blocking rules are unnecessary overhead in isolated test suites."

- **Interviewer:** "What happens if a migration fails during helper.runMigrationsAndValidate()?"
  **Answer:** "It throws an IllegalStateException with a detailed diff explaining which table, column, or index mismatched the expected schema JSON."

## Self-check rubric

Create an old schema fixture with edge-case rows, run each supported Room migration path, assert rows/indexes/foreign keys, and inject an exception inside a transaction to prove rollback. Name the Android runtime needed.

## References and reviewed-on date

- [Room migration testing](https://developer.android.com/training/data-storage/room/migrating-db-versions) — MigrationTestHelper and schemas.
- [Room withTransaction API](https://developer.android.com/reference/kotlin/androidx/room/package-summary) — local transactions.

Technically reviewed against primary documentation on 2026-10-13.
