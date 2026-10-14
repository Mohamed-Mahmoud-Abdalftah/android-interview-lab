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

Investigate R8 obfuscation stripping Entity properties or default constructors, unexpected Auto Backup restoring stale databases from Google Cloud, fallbackToDestructiveMigration wiping data on version mismatches, or Android Keystore master keys becoming invalidated between app launches in release builds.

## Interview answer — structured

A release-only database disappearance that succeeds in debug points to production compilation transforms or platform backup mechanisms.

First, with R8 / ProGuard Obfuscation, r8 processes release builds aggressively. If Entity classes or TypeConverters lack keep rules (`@Keep` or `-keep @androidx.room.Entity class * { *; }`), R8 renames fields or strips reflective no-arg constructors. Room may fail to deserialize existing rows on subsequent launches, failing silently or catching an internal reflection error and returning empty datasets. Next, with Android Auto Backup Collision, if `android:allowBackup="true"` is enabled in `AndroidManifest.xml`, the OS can restore an older cloud backup over the SQLite database file during installation or app restoration, replacing the newly written database with a stale snapshot.
Additionally, with Silent Destructive Migration, if the release build has an unversioned migration gap and `fallbackToDestructiveMigration()` is active, Room wipes the entire SQLite file on startup rather than crashing with an `IllegalStateException`. Finally, with Keystore Invalidation (SQLCipher / Encrypted DBs), if the database is encrypted, ensure the master key in Android Keystore wasn't flagged with `setUserAuthenticationRequired(true)` or invalidated by device lockscreen configuration changes.


## Interview answer — deep senior

To diagnose this systematically in production.

First, with Inspect the Physical SQLite File, using Android Studio Device File Explorer or an internal debug menu on a signed release build, inspect `/data/data/<package>/databases/app.db`. Check file size and dump table contents via the `sqlite3` CLI tool to verify if rows were committed to disk. Next, with Verify WAL (Write-Ahead Logging) Checkpoints, SQLite WAL mode writes transactions into a separate `app.db-wal` file. If the process is killed abruptly before a WAL checkpoint completes and the app configuration disables WAL on restart, uncheckpointed transactions can disappear.
Finally, with Rule Out Optimistic UI Illusions, ensure the repository actually committed the transaction to SQLite rather than only updating a MutableStateFlow in memory.


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
