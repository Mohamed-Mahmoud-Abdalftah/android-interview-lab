---
id: "SEC-23"
question: "What are the threats of insecure backup and local database files?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 320
editorial_status: "reviewed"
---

# SEC-23

## Original interview question

What are the threats of insecure backup and local database files?

## What the interviewer evaluates

- Backup and database-file exposure despite normal sandboxing.
- Android-version-specific extraction rules and Keystore restore mismatch.

## Explanation in Arabic

ما هي التهديدات الأمنية المترتبة على النسخ الاحتياطي غير الآمن (Insecure Backup) وملفات قواعد البيانات المحلية غير المشفرة؟

1. تهديد النسخ الاحتياطي المحلي و السحابي (Insecure Backups):
   - **ADB Backup Extraction**: في التطبيقات التي تترك `android:allowBackup="true"` في الـ Manifest، يمكن لأي شخص يملك وصولاً فيزيائياً للهاتف عبر كابل USB تفعيل USB Debugging وتنفيذ أمر:
     `adb backup -f backup.ab com.example.app`.
   - هذا الأمر يستخرج ملفات التطبيق الخاصة بالكامل (SharedPreferences, Databases, Caches) إلى جهاز الكمبيوتر بدون الحاجة لصلاحيات Root!
   - **Android Cloud Backup**: رفع ملفات التطبيق إلى حساب Google Drive الخاص بالمستخدم. إذا تم اختراق حساب Google أو استرجاع النسخة على جهاز آخر، قد تتسرب البيانات أو تتعطل التشفيرات.

2. تهديد قواعد البيانات المحلية غير المشفرة (Plaintext SQLite / Room):
   - ملفات قواعد البيانات (`/data/data/<package>/databases/app.db`) تخزن الجداول والنصوص كـ Plaintext.
   - أي تطبيق خبيث يستغل ثغرة في النظام أو جهاز معمول له Root يستطيع نسخ الملف وفتحه باستخدام أي أداة SQLite Viewer وقراءة كل سجلات المعاملات، الحسابات، والبيانات الشخصية (PII).

3. الحلول الهندسية الموصى بها:
   - تعطيل النسخ الاحتياطي في الـ Manifest (`android:allowBackup="false"`) أو تخصيص قواعد استثناء صارمة عبر `backup_rules.xml`.
   - تشفير قاعدة البيانات بالكامل باستخدام **SQLCipher** المدمج مع Android Room Database.
   - حفظ مفتاح تشفير قاعدة البيانات داخل Android Keystore بدلاً من كتابته كنص صريح في الكود.

## Practical walkthrough

تأمين قواعد بيانات Room باستخدام SQLCipher وتعطيل النسخ الاحتياطي الحساس:
```kotlin
// 1. بناء قاعدة بيانات Room مشفرة بالكامل عبر SQLCipher بمفتاح من Keystore:
class EncryptedDatabaseProvider(
    private val context: Context,
    private val keyStoreManager: KeystoreSecretStorage
) {
    fun buildEncryptedRoomDatabase(): AppDatabase {
        // استرجاع مصفوفة بايتات مفتاح التشفير من الـ Keystore المشفر
        val dbPassphrase = keyStoreManager.getOrCreateDatabasePassphrase()
        
        // إنشاء SupportFactory الخاص بمكتبة SQLCipher:
        val supportFactory = SupportFactory(dbPassphrase)

        return Room.databaseBuilder(context, AppDatabase::class.java, "secure_app_vault.db")
            .openHelperFactory(supportFactory) // تفعيل تشفير SQLCipher AES-256 بالكامل لملف الداتابيز
            .build()
    }
}
```

```xml
<!-- 2. حماية الـ Manifest واستثناء البيانات الحساسة من النسخ الاحتياطي -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application
        android:allowBackup="false"
        android:fullBackupContent="false"
        android:dataExtractionRules="@xml/secure_backup_rules">
    </application>
</manifest>
```

## Why it matters and how it works

Android Auto Backup may include app data by default; rules differ for Android 12+ target behavior versus older backup XML. Database files and WAL/journal files should be reviewed together. File encryption and backup exclusion are separate controls, and `allowBackup`/data extraction configuration must be tested on supported versions.

## Worked example

A POS app stores only masked card display data and transaction operation IDs in Room. It excludes token/ciphertext files from cloud backup, restores transaction history from the backend, and tests device transfer. If it stores an encrypted local queue, the queue’s recovery rules must not assume its Keystore key follows it.

## Trade-offs and decision criteria

Backup improves user recovery, while exclusion limits exposure and avoids undecryptable restores. Server resync may be preferable for financial records; offline queues need durable local data plus a recovery and reconciliation strategy.

## Failure modes

An app excludes the main DB but leaves a WAL or export file containing sensitive rows, or backs up ciphertext without its key. Inventory all files and run backup/restore tests across API versions; do not infer behavior from one manifest flag.

## Production perspective

Production security review inspects database schema, cache files, WAL, exports and backup rules, and verifies a real restore. Account/session data is reauthenticated, while authoritative payment history is obtained from the server.

## Interview answer — short

Insecure backups allow full sandbox extraction via adb backup or Google Drive sync if allowBackup is enabled. Unencrypted SQLite databases leave records readable in plaintext. Remediate by disabling allowBackup or setting strict extraction rules, and encrypting databases at rest using SQLCipher with Keystore-derived passphrases.

## Interview answer — structured

Local storage vulnerabilities stem from assumptions about sandbox persistence and physical isolation.

First, **Insecure Backup Vulnerabilities**. Next, if `android:allowBackup="true"` is present in `AndroidManifest.xml`, an attacker with physical access and USB debugging enabled can run `adb backup` to extract the entire application sandbox—including shared preferences, cached HTTP responses, and SQLite databases—into a plaintext tar archive on a desktop machine.
In cloud backups, sensitive data syncs to the user's Google Drive, where it may be exposed to secondary account compromise. **Unencrypted Database Risks**.
Standard Room / SQLite databases store records in plaintext binary pages. Anyone with root access, physical flash extraction tools, or system debugging privileges can run `sqlite3` on `/data/data/<package>/databases/` to inspect transaction histories and PII. **Defensive Architecture**.
Set `android:allowBackup="false"` for security-critical apps, or define granular `dataExtractionRules` excluding all databases and datastores. Finally, encrypt databases using **SQLCipher for Android**, passing a 256-bit passphrase derived from Android Keystore directly into Room's `SupportFactory`.


## Interview answer — deep senior

From a compliance and forensics perspective, securing data-at-rest requires comprehensive storage hygiene.

First, a SQLCipher Key Management is the security of SQLCipher is entirely dependent on its encryption key. Hardcoding a passphrase in Kotlin or using a static salt renders SQLCipher completely ineffective against reverse engineering. The passphrase must be generated randomly on first launch, encrypted using an `AndroidKeyStore` AES-GCM master key, and loaded into memory only during database initialization. Next, with Database Wal & Journal Leaks, SQLite uses Write-Ahead Logging (WAL) and rollback journals (`.db-wal` and `.db-shm`). When SQLCipher is used, WAL files are also encrypted under the same cipher. However, if unencrypted SQLite is used, deleting rows does not immediately wipe data from disk pages until a `VACUUM` command is issued, leaving deleted records recoverable in forensic memory scraps.
Finally, with Scoped Storage Realities, never store databases or sensitive temporary export files in shared public storage (`/sdcard/` or `MediaStore`). Maintain all sensitive relational and file stores strictly within internal application directory spaces (`context.filesDir`, `context.noBackupFilesDir`).


## How to answer in the interview

- **Why:** storage paths extend beyond the main database file.
- **How:** inventory DB, WAL, cache, SDK files, backup and transfer behavior.
- **Trade-off:** exclusions reduce restore convenience.
- **Failure case:** ciphertext restores without its local key or PAN leaks via WAL.
- **Production solution:** minimize rows and run real backup/restore tests.

## Deep-dive talking points

Prompt for WAL/journal inventory, Android 12+ rules, restore drill, Keystore mismatch and backend resync.

## Follow-up questions

- **Interviewer:** "What is the purpose of context.noBackupFilesDir?"
  **Answer:** "It provides a private filesystem directory whose contents are guaranteed to never be backed up to the cloud, regardless of manifest backup settings."

- **Interviewer:** "Does SQLCipher introduce performance overhead in Room?"
  **Answer:** "Yes, page-level AES encryption/decryption introduces approximately 5-15% overhead on heavy read/write database transactions."

## Self-check rubric

Can I identify database side files, backup rules, restore behavior and authoritative history recovery?

## References and reviewed-on date

- [Android Auto Backup](https://developer.android.com/identity/data/autobackup) — inclusion/exclusion and API behavior.
- [OWASP backup test](https://mas.owasp.org/MASTG/tests/android/MASVS-STORAGE/MASTG-TEST-0216/) — sensitive backup exposure.

Technically reviewed against primary documentation on 2026-10-13.
