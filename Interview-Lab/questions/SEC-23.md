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

## Concept and technical explanation

Insecure local database storage and unmanaged Android Auto Backup configurations expose sensitive enterprise data to extraction through device-to-device transfers, cloud backups, and local administrative attacks. By default, Android Auto Backup and adb backup target an application's entire private storage directory (/data/data/<package_name>), uploading databases, shared preferences, and cache files to the user's Google Drive. If an application stores sensitive records (PII, authentication tokens, payment history) in unencrypted SQLite or Room databases, an attacker who obtains a backup archive or accesses a backed-up Google Drive account gains full plaintext access. Furthermore, if an application encrypts its local databases using Android Keystore keys but permits Auto Backup, restoring the backup onto a new device results in permanent data corruption: the database files transfer over, but the hardware-backed Keystore keys remain trapped on the original device, causing unrecoverable decryption crashes. Applications must harden backup rules via data_extraction_rules.xml and encrypt Room databases with SQLCipher.

## Practical walkthrough (English)

Hardening backup rules and configuring SQLCipher for Room database encryption:
```xml
<!-- 1. Enforce strict data extraction rules in res/xml/data_extraction_rules.xml -->
<?xml version="1.0" encoding="utf-8"?>
<data-extraction-rules>
    <cloud-backup>
        <!-- Completely exclude sensitive databases and Keystore-dependent preferences -->
        <exclude path="databases/user_credentials.db" />
        <exclude path="databases/user_credentials.db-wal" />
        <exclude path="databases/user_credentials.db-shm" />
        <exclude path="shared_prefs/auth_session.xml" />
    </cloud-backup>
    <device-transfer>
        <exclude path="databases/user_credentials.db" />
        <exclude path="databases/user_credentials.db-wal" />
    </device-transfer>
</data-extraction-rules>
```
Configuring SQLCipher with Room:
```kotlin
// 2. Encrypting local Room database with SQLCipher SupportFactory
val passphraseBytes = getOrGenerateDatabasePassphraseFromKeystore()
val factory = SupportFactory(passphraseBytes)

val secureDatabase = Room.databaseBuilder(
    context,
    SecureAppDatabase::class.java,
    "user_credentials.db"
).openHelperFactory(factory)
 .build()
```

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

Unencrypted databases allow attackers to extract sensitive data via adb backup, physical theft, or cloud backup archives. Furthermore, restoring Keystore-encrypted files onto new devices causes fatal decryption crashes because hardware keys do not transfer. We mitigate this by excluding sensitive databases from backups via data_extraction_rules and encrypting Room with SQLCipher.

## Interview answer — structured

Insecure local database files and default backup configurations expose sensitive application data to extraction beyond the protection of the application sandbox.
By default, Android Auto Backup uploads application data to Google Drive and enables device-to-device migrations.
If an application stores personally identifiable information, session tokens, or transaction logs in standard unencrypted Room or SQLite databases, anyone with access to the backup archive or adb debugging can inspect the files in plaintext.
A more insidious operational hazard arises when apps encrypt local files using Android Keystore but fail to disable backups.
Because hardware-backed Keystore keys are bound to physical chips and never migrate across devices, restoring the encrypted database on a new phone leaves the application with orphan ciphertext, causing crashes and permanent data loss.
To mitigate these threats, applications must configure data_extraction_rules to exclude sensitive database files and journals from cloud backups, while encrypting Room databases at rest using SQLCipher with keys protected in Android Keystore.

## Interview answer — deep senior

In mobile threat modeling, the boundary of the local application sandbox is porous when considering backups and offline disk analysis.
Many developers assume that because /data/data requires root access to read, unencrypted SQLite databases are safe from unauthorized extraction.
However, if android:allowBackup is enabled without granular extraction rules, an adversary with physical access can enable USB debugging and execute adb backup to extract the entire private storage tree into an unencrypted tarball.
Even without USB debugging, Android Auto Backup routinely archives application files to Google Drive.
If a user's cloud account is compromised through phishing or credential stuffing, the attacker downloads the full application database, exposing sensitive personal records and financial logs.
Furthermore, the clash between Auto Backup and Android Keystore represents one of the most common causes of unrecoverable production database corruption.
When a user switches to a new phone, the OS restores the encrypted database file, but the hardware-backed key required to decrypt it was destroyed with the old device.
When Room initializes with SQLCipher, the open helper fails with a file is not a database error, crashing the application on startup.
Senior architecture mandates two explicit controls.
At the OS policy layer, in res/xml/data_extraction_rules.xml, we explicitly exclude all database files, including SQLite Write-Ahead Logging (.wal) and shared-memory (.shm) journal files, from both cloud backups and device transfers.
Second, we encrypt Room databases at rest using SQLCipher, wrapping the database encryption passphrase with an Android Keystore master key and treating local storage strictly as an ephemeral, re-syncable cache of backend truth.

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
