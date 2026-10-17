---
id: "DAT-18"
question: "A transaction is saved but disappears after restart in release builds only. What should you investigate?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "C"
phase: 3
priority: "P1"
order: 275
editorial_status: "reviewed"
---

# DAT-18

## Original interview question

A transaction is saved but disappears after restart in release builds only. What should you investigate?

## What the interviewer evaluates

Investigate release-only disappearance of saved transaction across persistence, R8, encryption and backup paths.

## Concept and technical explanation

Investigating release-only data disappearance requires systematically auditing build-variant configuration, code shrinking, and SQLite lifecycle behaviors:
- In-Memory Database Configuration: Check dependency injection modules (Hilt/Koin). A common mistake is injecting Room.inMemoryDatabaseBuilder() in release due to a flipped BuildConfig.DEBUG check, causing SQLite tables to reside solely in RAM and vanish on process death.
- ProGuard/R8 Obfuscation & Reflection Stripping: R8 shrinks, obfuscates, or strips default constructors, getters/setters, or @TypeConverter classes if proper keep rules are missing. While Room generates code at compile time, reflection-based converters or obfuscated entity column names can fail silently, leading Room to deserialize empty defaults upon app relaunch.
- Silent Destructive Migration: If the release build increments the database schema version without registering a corresponding Migration, and fallbackToDestructiveMigration() was enabled, Room silently drops and recreates all tables on startup.
- SQLite WAL Journaling & Unclosed Transactions: In Write-Ahead Logging mode, writes reside in the -wal file. If transactions are never committed, or if the database is opened from cache directories that the OS periodically clears, persisted records disappear after app termination.

## Practical walkthrough (English)

Verifying dependency injection, ProGuard rules, and migration configurations:
```kotlin
// 1. Audit DI Module: ensure disk database is consistently configured
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "production_app.db" // Guard against accidental inMemoryDatabaseBuilder
        )
        // Strictly forbid destructive migrations in release builds
        .apply {
            if (BuildConfig.DEBUG) {
                fallbackToDestructiveMigration()
            }
        }
        .build()
    }
}

// 2. Audit ProGuard / R8 Rules: protect entities and converters from stripping
// -keepclassmembers class * extends androidx.room.RoomDatabase {
//     <init>();
// }
// -keep class com.example.data.local.entities.** { *; }
// -keep class * extends androidx.room.TypeConverter { *; }
```

## Explanation in Arabic

المعاملة تُحفظ في قاعدة البيانات وتعمل بنجاح في Debug، لكنها تختفي تماماً بعد إعادة تشغيل التطبيق في Release Builds فقط! كيف تشخص وتصلح هذه المشكلة الغامضة؟

1. تشريح أسباب الاختلاف بين Debug و Release (Root Cause Analysis):
   - المشكلة لا تحدث في Debug ولكنها تحدث في Release دائماً ترتبط بأحد العوامل التالية:
     * **قواعد R8/ProGuard وتحسينات الـ Bytecode**: قام R8 بحذف الـ No-Arg Constructor أو تغيير أسماء الحقول عبر الـ Obfuscation، مما جعل Room أو مكتبة التشفير تعجز عن قراءة البيانات بعد إعادة التشغيل.
     * **ميزة النسخ الاحتياطي التلقائي (Android Auto Backup & GMS Restore)**: في ملف `AndroidManifest.xml`، إعداد `android:allowBackup="true"` يقوم باستعادة قاعدة بيانات قديمة فارغة من Google Cloud عند إعادة تثبيت نسخة Release!
     * **فقدان مفاتيح التشفير في Android Keystore (SQLCipher / EncryptedSharedPreferences)**: يتم توليد مفتاح التشفير في الذاكرة ولكن يفشل حفظه أو استعادته من الـ Keystore بسبب عدم توفر قواعد حماية R8 للكلاسات المشفرة.
     * **استدعاء `fallbackToDestructiveMigration()` بالخطأ في Release**: اختلاف في رقم الإصدار بين ملفات الـ Schema أدى لمسح قاعدة البيانات بهدوء عند الإقلاع.

2. خطة التحقيق التشخيصية المنظمة:
   - فحص هل البيانات كُتبت فعلياً في ملف SQLite أم كانت معروضة كـ Optimistic UI State فقط في الـ ViewModel.
   - فحص سجلات Logcat في نسخة Release موقّعة (`release` build مع `debuggable = true` مؤقتاً لتتبع الـ Crash).
   - مراجعة ملف `proguard-rules.pro` وإضافة قواعد الحماية لكلاسات الـ Entity والـ Room.

## Practical walkthrough

خطوات إصلاح وتأمين كلاسات Room ونظام التخزين ضد مشاكل R8 والـ Backup:
```kotlin
// 1. تأمين كلاسات Entity ضد R8 Obfuscation في proguard-rules.pro:
// لو قام R8 بتغيير أسماء الحقول، تعجز SQLite عن مطابقة الأعمدة:
-keepclassmembers class * extends androidx.room.RoomDatabase {
    public void clearAllTables();
}
-keep class * extends androidx.room.RoomDatabase
-keep @androidx.room.Entity class * { *; }
-keep class * implements androidx.room.migration.Migration { *; }

// 2. منع استعادة النسخ الاحتياطية القديمة من السحابة في AndroidManifest.xml:
// <application
//     android:allowBackup="false"
//     android:fullBackupContent="false" ... />

// 3. التحقق البرمجي من أن fallbackToDestructiveMigration غير مفعل:
Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
    .addMigrations(MIGRATION_1_2, MIGRATION_2_3)
    // ❌ احذر تماماً من كتابة هذا السطر في Release:
    // .fallbackToDestructiveMigration() // هذا يمسح قاعدة البيانات إذا لم يجد مسار ترحيل!
    .build()
```

## Why it matters and how it works

Build a timeline: local transaction commit, process death, reopen, query, session filter and sync overwrite. Inspect release variant schema/version, shrinker mapping, manifest, encryption key/backup configuration and server reconciliation. Preserve evidence and redact financial data. A local row disappearing may reflect wrong account partition, sync deletion or database reset.

## Worked example

Conceptual diagnostic check; app DAO/model are product types, and telemetry should log IDs/status only.

```kotlin
suspend fun verifyAfterSave(dao: TransactionDao, id: String) {
    dao.insertPending(id)
    val observed = dao.findById(id)
    check(observed != null) { "pending row missing after local insert: $id" }
}
// Repeat read after force-stop/relaunch with the signed release variant.
```

## Trade-offs and decision criteria

Instrumented release tests with minification catch variant-only behavior but cost more CI time. A migration test catches schema/data loss, while R8 mapping/retrace helps diagnose reflective failures. Do not disable shrinking as a permanent unexplained workaround.

## Failure modes

Optimistic UI can show Saved before the DAO transaction commits. A destructive migration can silently wipe rows on upgrade. A restore can bring encrypted DB without its key, or logout can delete account partition. A release-only serializer failure can map the wrong columns/payload.

## Production perspective

A payments app logs stable operation IDs and local state transitions, reproduces a signed release upgrade/force-stop, inspects DB and reconciles server state. It freezes destructive cleanup until root cause is known and tests each suspected boundary.

## Interview answer — short

Investigating release-only data loss requires auditing four root causes: verifying dependency injection does not inject an in-memory database, ensuring R8 shrinking does not strip Room entity constructors or TypeConverters, confirming fallbackToDestructiveMigration is disabled, and verifying the database file is stored in permanent app files rather than volatile cache directories.

## Interview answer — structured

Diagnosing data disappearance that reproduces exclusively in release builds requires isolating compilation, dependency injection, and storage discrepancies.
First, audit the dependency injection module. A flipped boolean condition in Hilt or Koin often accidentally injects Room.inMemoryDatabaseBuilder instead of the disk database in release, causing tables to evaporate whenever the process dies.
Second, examine R8 and ProGuard rules. Aggressive code shrinking can strip no-arg entity constructors or custom TypeConverters, causing Room to silently fail deserialization upon cold restart and return empty default records.
Third, verify database migration declarations. If release bumped the database version without an explicit migration and fallbackToDestructiveMigration was configured, Room silently drops and recreates SQLite tables on startup.
Fourth, ensure the database file resides in internal storage rather than temporary cache directories that Android purges under memory pressure.

## Interview answer — deep senior

When a critical transaction persists during the session but vanishes after app restart exclusively in release builds, senior engineers immediately suspect build configuration differences rather than standard runtime database logic.
Our first investigation step is examining dependency injection graphs in Hilt.
We frequently find teams wrapping database creation in conditional logic where release accidentally receives an in-memory database builder, meaning SQLite writes exist only in volatile process RAM and vanish on process death.
The second critical area is R8 code shrinking and optimization.
Because release builds execute minification, if entity data classes or TypeConverters lack proper keep annotations, R8 can strip field getters, setters, or synthetic constructors that Room relies on during deserialization.
This causes Room queries to return default null values after restart without crashing.
The third and most catastrophic culprit is silent destructive migration.
If the release version increments the database schema number without registering a corresponding Migration object, and someone left fallbackToDestructiveMigration enabled, Room detects the schema mismatch during launch, drops all tables, and recreates an empty database.
Finally, we verify storage location and WAL journal flushing: we ensure the database is stored in context.filesDir, and confirm background write transactions are cleanly committed before the process enters background, preventing uncheckpointed Write-Ahead Logging state from getting discarded.

## How to answer in the interview

- **Why:** “Saved then gone” crosses UI, DB, sync, migration and backup boundaries.
- **How:** Build a commit-to-restart timeline with safe IDs/schema telemetry.
- **Trade-offs:** Keep diagnostic detail without sensitive payload logging.
- **Failure cases:** Destructive fallback, premature worker deletion or lost encryption key.
- **Production solution:** Reproduce in minified release and test each crash window.

## Deep-dive talking points

Trace write/commit/reopen/filter/sync steps and distinguish release variant causes by evidence.

## Follow-up questions

- **Interviewer:** "How do you verify whether R8 caused the bug?"
  **Answer:** "Enable R8 mapping tracing or build a release APK with `minifyEnabled false` and test whether the bug disappears."

- **Interviewer:** "How do you disable automatic cloud backup of your SQLite database specifically?"
  **Answer:** "Specify an XML backup rules file (`android:fullBackupContent="@xml/backup_rules"`) and add `<exclude domain="database" path="app.db"/>`."

## Self-check rubric

Can I prove commit, inspect exact release artifact and rule causes in/out without guessing?

## References and reviewed-on date

- [Android Room migrations](https://developer.android.com/training/data-storage/room/migrating-db-versions) — migration data preservation.
- [Android R8 overview](https://developer.android.com/build/shrink-code) — release shrinking behavior.

Technically reviewed against primary documentation on 2026-10-13.
