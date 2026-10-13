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

Design data-preserving Room migrations by enabling exported schemas, writing explicit SQL migrations (ALTER TABLE or temp-table copy patterns), never defaulting to destructive fallback in production, and verifying migration paths from older versions using Room's MigrationTestHelper.

## Interview answer — structured

Preserving user data during Room schema evolution requires treating database migrations with the same rigor as backend database upgrades:

1. **Export Schemas via Gradle**: Configure `room.schemaLocation` in `build.gradle.kts` and commit generated schema JSON files to Git. This provides Room with the baseline schema for every released version.

2. **Explicit Migration Scripts**: Avoid `fallbackToDestructiveMigration()` in production offline-first apps, which completely drops tables and purges pending user drafts. Write explicit `Migration(from, to)` objects containing valid SQLite DDL.

3. **Handling Complex Schema Changes**: Because SQLite historically has limited `ALTER TABLE` support (e.g. dropping columns or altering constraints), use the **Table Recreation Pattern**: create the new table with desired schema, copy data over (`INSERT INTO new SELECT ... FROM old`), drop the old table, and rename the new table.

4. **Automated Migration Testing**: Use `MigrationTestHelper` in instrumented or Robolectric tests. The test spins up version $N$, inserts test records, executes the migration to $N+1$, and asserts that rows exist and columns match expected types.

## Interview answer — deep senior

A critical production hazard is **Sparse Version Upgrades**.

Users rarely update apps sequentially. A user might jump directly from app version 1.0 (Database version 1) to app version 4.0 (Database version 5). Room allows defining discrete incremental migrations (`1->2`, `2->3`, `3->4`, `4->5`) and chains them automatically at startup. However, if any link in the chain is missing, Room crashes with an `IllegalStateException`.

To bulletproof release rollouts:
- Implement continuous CI tests verifying every supported upgrade path (e.g. test `1->5`, `2->5`, `3->5`).
- If table recreation involves millions of rows, run migrations within a transaction and monitor disk space, as SQLite requires temporary storage equal to the table size during table copy operations.

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
