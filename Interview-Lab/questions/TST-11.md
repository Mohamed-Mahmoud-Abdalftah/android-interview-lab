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

Test Room DAOs using in-memory databases with allowMainThreadQueries() to ensure rapid, isolated tests. Test database migrations using Room's MigrationTestHelper in instrumented tests, verifying that existing records are preserved and new schema constraints match versioned schema JSON files.

## Interview answer — structured

Room database testing divides into DAO functional validation and schema migration verification:

1. **In-Memory DAO Testing**:
   - Instantiate tests using `Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java).allowMainThreadQueries().build()`.
   - In-memory databases exist strictly in RAM and are completely destroyed upon `db.close()`, guaranteeing test isolation without disk file leftovers.
   - Test reactive DAO flows using Turbine to assert that SQL inserts/updates emit fresh lists to active flow collectors.

2. **Automated Migration Testing (`MigrationTestHelper`)**:
   - Use Room's `MigrationTestHelper` in instrumented tests.
   - Step 1: `helper.createDatabase(DB_NAME, 1)` boots SQLite using the version 1 JSON schema. Insert sample records via raw SQL.
   - Step 2: `helper.runMigrationsAndValidate(DB_NAME, 2, true, MIGRATION_1_2)` applies the migration and automatically validates SQLite column types and foreign keys against the version 2 JSON schema.
   - Step 3: Query the migrated database to assert that historical records survived uncorrupted and new columns received default values.

3. **Transaction Atomicity Verification**:
   - Test methods marked `@Transaction`. Inject an intentional exception halfway through a batch operation, and assert that previously written rows in that transaction were rolled back completely.

## Interview answer — deep senior

From an enterprise storage engineering perspective, database tests must validate SQLite constraints and threading boundaries:

1. **Foreign Key Constraint Verification**: By default, SQLite disables foreign key enforcement unless explicitly enabled via `PRAGMA foreign_keys = ON;`. In-memory tests must configure Room callbacks or open helper factories to enable foreign keys, ensuring tests catch constraint violations before production.

2. **Multi-Version Migration Chains (v1 -> v4)**: Write automated test permutations that test direct multi-version hops (`1->4`) alongside sequential hops (`1->2->3->4`), verifying that legacy users upgrading across multiple years do not encounter `IllegalStateException` on launch.

3. **Robolectric SQLite vs. Real Device SQLite**: While Robolectric runs SQLite tests on the host machine using SQLite4Java or native macOS/Linux SQLite libraries, OEM Android devices run customized SQLite engines. Always execute complex migration and WAL concurrency tests on real Android instrumented test runners.

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
