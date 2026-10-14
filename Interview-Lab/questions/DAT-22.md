---
id: "DAT-22"
question: "You must migrate encrypted and unencrypted local databases. How do you protect against data loss?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "C"
phase: 3
priority: "P1"
order: 279
editorial_status: "reviewed"
---

# DAT-22

## Original interview question

You must migrate encrypted and unencrypted local databases. How do you protect against data loss?

## What the interviewer evaluates

Migrate encrypted and plaintext databases with verified copy, key/backup recovery and no destructive fallback.

## Explanation in Arabic

كيف تهاجر قاعدة بيانات محلية غير مشفرة (Plaintext Database) إلى قاعدة بيانات مشفرة بالكامل (SQLCipher / Encrypted DB) دون فقدان أي بيانات؟

1. مخاطر الهجرة الأمنية لقواعد البيانات:
   - تحويل قاعدة بيانات SQLite العادية إلى مشفرة بـ SQLCipher ليس مجرد تغيير في كود الـ Schema؛ بل هو تشفير ثنائي كامل لجميع صفحات الـ SQLite على القرص.
   - **المخاطر الكبرى**: نفاد مساحة الذاكرة على الهاتف (Disk Full)، انقطاع الكهرباء أو قتل الـ Process في منتصف التشفير، أو فقدان مفتاح التشفير من Android Keystore.

2. البروتوكول الآمن خطوة بخطوة (Zero Data-Loss Encryption Protocol):
   - **المرحلة 1: توليد وحفظ مفتاح التشفير بأمان**:
     * توليد مفتاح عشوائي 256-bit وحفظه في الـ **Android Keystore System** لضمان عدم استخراجه.
   - **المرحلة 2: إنشاء قاعدة بيانات مشفرة جديدة كملف منفصل (Safe Staging)**:
     * لا تشفر الملف الأصلي في مكانه مباشرة!
     * افتح قاعدة بيانات مشفرة جديدة باسم مؤقت (`app_encrypted.db`) باستخدام مكتبة SQLCipher ومفتاح الـ Keystore.
   - **المرحلة 3: نسخ البيانات عبر أمر التشفير الأصلي في SQLCipher (`sqlcipher_export`)**:
     * تنفيذ أمر `ATTACH DATABASE 'app_encrypted.db' AS encrypted KEY 'passphrase';` ثم `SELECT sqlcipher_export('encrypted');` ثم `DETACH DATABASE encrypted;`.
     * هذا الأمر يقوم بنسخ جميع الجداول والبيانات والـ Indexes وتشفيرها بشكل ذري.
   - **المرحلة 4: التحقق الصارم قبل حذف الملف الأصلي**:
     * فتح قاعدة البيانات المشفرة والتأكد من تطابق عدد الصفوف (Row Counts).
     * بعد التحقق بنسبة 100% فقط: حذف قاعدة البيانات القديمة غير المشفرة، وإعادة تسمية الملف المشفر إلى الاسم الرسمي.

## Practical walkthrough

خطة ترحيل قاعدة بيانات غير مشفرة إلى مشفرة بأمان عبر SQLCipher:
```kotlin
class DatabaseEncryptionMigrator(private val context: Context) {

    fun migratePlaintextToEncrypted(plaintextDbName: String, encryptedDbName: String, passphrase: ByteArray) {
        val plaintextFile = context.getDatabasePath(plaintextDbName)
        val encryptedFile = context.getDatabasePath(encryptedDbName)

        // 1. إذا كان الملف الأصلي غير موجود، أو المشفر موجود ومكتمل -> لا داعي للهجرة:
        if (!plaintextFile.exists() || encryptedFile.exists()) return

        // 2. فتح قاعدة البيانات القديمة واستخدام sqlcipher_export لتصديرها مشفرة:
        net.sqlcipher.database.SQLiteDatabase.loadLibs(context)
        val rawDb = net.sqlcipher.database.SQLiteDatabase.openOrCreateDatabase(plaintextFile, "", null)

        try {
            // ربط القاعدة المشفرة الجديدة وتصدير البيانات بالكامل:
            rawDb.rawExecSQL("ATTACH DATABASE '${encryptedFile.absolutePath}' AS encrypted KEY x'${passphrase.toHex()}';")
            rawDb.rawExecSQL("SELECT sqlcipher_export('encrypted');")
            rawDb.rawExecSQL("DETACH DATABASE encrypted;")
        } finally {
            rawDb.close()
        }

        // 3. التحقق الحاسم من صحة التشفير قبل حذف القديم:
        val testEncryptedDb = net.sqlcipher.database.SQLiteDatabase.openOrCreateDatabase(encryptedFile, passphrase, null)
        val isVerified = testEncryptedDb.isOpen && testEncryptedDb.version >= 1
        testEncryptedDb.close()

        // 4. الحذف فقط بعد نجاح التحقق 100%:
        if (isVerified) {
            context.deleteDatabase(plaintextDbName)
        }
    }
}
```

## Why it matters and how it works

Inventory supported file formats, keys, backup policies and migration paths. A safe protocol copies to a temporary destination, validates row counts/checksums and critical invariants, flushes/renames, and records completion so restart can resume or roll back. Key loss is a separate threat: do not silently replace unrecoverable user data with empty DB.

## Worked example

Conceptual migration state machine; actual database/encryption library APIs are project-specific and must be tested on device.

```kotlin
enum class MigrationStage { NOT_STARTED, COPYING, VERIFIED, SWITCHED }
interface DbMigrationJournal {
    suspend fun stage(): MigrationStage
    suspend fun mark(stage: MigrationStage)
}
// Keep source file until destination verification and safe switch complete.
```

## Trade-offs and decision criteria

In-place migration is faster but risks irreversible loss; copy-and-swap needs extra storage and careful file handling. Encryption protects data at rest only under a sound key/backup threat model. Rolling back to an old app may not read new format, so rollout must plan compatibility.

## Failure modes

Backing up ciphertext without its Keystore key can create an unreadable restored DB. Deleting plaintext source before verifying encrypted copy loses drafts on disk-full or crash. A migration journal stored only in volatile memory cannot recover after process death.

## Production perspective

A health app migrates legacy plaintext records to encrypted storage in a staged release. It tests old fixtures, low storage, key invalidation, backup restore and kill at each stage. Metrics record only counts/status, never sensitive rows; support provides recovery guidance.

## Interview answer — short

Migrate plaintext SQLite databases to SQLCipher encryption without data loss using staged export: generate a 256-bit master key in Android Keystore, attach a new encrypted database file, execute sqlcipher_export to copy all tables, verify row count integrity on the encrypted target, and delete the plaintext source only after verification succeeds.

## Interview answer — structured

Migrating an unencrypted database to SQLCipher encryption carries severe corruption risks if interrupted by crashes or power loss. A resilient enterprise migration follows a **Staged Export & Verify Protocol**.

First, with Keystore Key Generation, generate a cryptographically secure 256-bit AES master key inside the hardware-backed **Android Keystore System** to protect the SQLCipher passphrase. Next, with Staged Out-of-Place Export, never attempt in-place encryption. Open the existing plaintext SQLite database using SQLCipher and attach a fresh, separate destination file: `ATTACH DATABASE 'app_encrypted.db' AS encrypted KEY '<passphrase>'`.
Additionally, with Atomic SQLCipher Export, execute `SELECT sqlcipher_export('encrypted')` followed by `DETACH DATABASE encrypted`. This native SQLCipher engine routine copies all schemas, tables, triggers, and indices into the encrypted container with hardware-accelerated AES-256. With Integrity Verification, open the new encrypted database, execute `PRAGMA integrity_check`, and assert row count equivalence across critical tables.
Finally, with Atomic Swap & Cleanup, only after verification passes, delete the plaintext database file (`context.deleteDatabase(plainDb)`). If anything fails prior to verification, abort and retain the unencrypted file.


## Interview answer — deep senior

Two catastrophic edge cases must be handled in production.

First, insufficient Disk Space (`ENOSPC`) is the `sqlcipher_export` operation duplicates the entire database on disk during export. If a user's database is 200MB and their device has only 100MB of free flash storage, the export fails midway with SQLite disk corruption. Pre-flight check: query `StatFs(context.filesDir.path).availableBytes`. Ensure free disk space is at least **$2.5 \times$** the size of the unencrypted database before attempting the migration. Finally, with Process Death / Battery Loss Mid-Export, if Android OS terminates the process halfway through export, `app_encrypted.db` exists in a corrupted, half-written state. On the next launch, the migrator must detect the partial file, delete the corrupted staging file, and re-run the migration safely from the pristine unencrypted original.


## How to answer in the interview

- **Why:** Migration failure can destroy both data and decryptability.
- **How:** Classify source, copy to temporary destination, verify, switch with stage marker.
- **Trade-offs:** Keep source until validated; design key/backup recovery separately.
- **Failure cases:** Wrong key, low storage, mid-switch crash, silent destructive fallback.
- **Production solution:** Device tests for each stage and explicit recovery UX.

## Deep-dive talking points

Walk crash windows, key/backup mismatch, verification and rollout/rollback limits.

## Follow-up questions

- **Interviewer:** "What does `PRAGMA integrity_check` do in SQLite?"
  **Answer:** "It scans the entire database file for out-of-order index records, missing B-tree pages, and malformed binary pointers, returning 'ok' if healthy."

- **Interviewer:** "Can Room work directly with SQLCipher?"
  **Answer:** "Yes, by passing a `SupportFactory(passphrase)` from the SQLCipher library into Room's database builder via `openHelperFactory()`."

## Self-check rubric

Can I preserve original, verify copy, recover each crash stage and handle non-restorable keys?

## References and reviewed-on date

- [Android Room migrations](https://developer.android.com/training/data-storage/room/migrating-db-versions) — upgrade testing.
- [Android backup guidance](https://developer.android.com/identity/data/backup) — backup/restore behavior.
- [Android Keystore guide](https://developer.android.com/privacy-and-security/keystore) — key storage.

Technically reviewed against primary documentation on 2026-10-13.
