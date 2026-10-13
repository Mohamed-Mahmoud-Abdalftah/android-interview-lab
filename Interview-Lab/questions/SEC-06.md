---
id: "SEC-06"
question: "What are encryption at rest and encryption in transit?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "A"
phase: 3
priority: "P1"
order: 303
editorial_status: "reviewed"
---

# SEC-06

## Original interview question

What are encryption at rest and encryption in transit?

## What the interviewer evaluates

- Scope of confidentiality for stored bytes and network transport.
- Key handling, TLS endpoint validation, and plaintext at use time.

## Explanation in Arabic

ما هو التشفير في حالة السكون (Encryption at Rest) والتشفير في حالة النقل (Encryption in Transit) في Android؟

1. التشفير في حالة السكون (Encryption at Rest - حماية البيانات المخزنة):
   - **ما هو**: حماية البيانات المخزنة محلياً على ذاكرة الجهاز (Flash Storage / Disk) عند إغلاق التطبيق أو قفل الهاتف.
   - **مستوياته في Android**:
     * **تشفير مستوى النظام (File-Based Encryption - FBE)**: مدمج في Android 7.0+. يقسم الذاكرة إلى مساحتين مشفرتين بمفتاح الجهاز: مساحة `Device Encrypted (DE)` ومساحة `Credential Encrypted (CE)` التي لا تُفتح إلا بعد قيام المستخدم بإدخال رمز القفل (PIN/Password).
     * **تشفير مستوى التطبيق (App-Level Encryption)**: تشفير قواعد البيانات الحساسة (مثل Room عبر **SQLCipher**) ومفاتيح التفضيلات الحساسة عبر **Android Keystore** لضمان حمايتها حتى لو تم كسر حماية الـ FBE على جهاز Rooted.

2. التشفير في حالة النقل (Encryption in Transit - حماية البيانات أثناء السير عبر الشبكة):
   - **ما هو**: حماية حزم البيانات أثناء انتقالها عبر كابلات وأبراج الاتصالات وشبكات الـ Wi-Fi العامة بين الهاتف والسيرفر.
   - **كيف يُطبق في Android**:
     * استخدام **TLS 1.3 / HTTPS** الإلزامي.
     * حظر الاتصالات غير المشفرة (Cleartext HTTP) في `network_security_config.xml` (`cleartextTrafficPermitted="false"`).
     * تطبيق **Certificate Pinning** لمنع هجمات Man-In-The-Middle (MITM) إذا قام المهاجم بتثبيت شهادة Root خبيثة على الهاتف.

3. الثغرة المشتركة (The Plaintext in Use Window):
   - كلا النوعين يحميان البيانات وهي مخزنة أو وهي مسافرة، لكن عند استخدامها داخل كود Kotlin، تكون البيانات **Plaintext في ذاكرة الـ RAM**! يجب مسح المخازن المؤقتة الحساسة بعد استخدامها فوراً.

## Practical walkthrough

تطبيق التشفير في السكون (SQLCipher) والتشفير في النقل (Network Security Config):
```xml
<!-- 1. التشفير في النقل: منع الـ Cleartext HTTP وفرض TLS في res/xml/network_security_config.xml -->
<network-security-config>
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" /> <!-- الثقة في شهادات النظام فقط وحظر شهادات المستخدم في Release -->
        </trust-anchors>
    </base-config>
</network-security-config>
```

```kotlin
// 2. التشفير في السكون: تشفير ملف قاعدة بيانات Room بالكامل عبر SQLCipher بمفتاح من Keystore:
val passphrase = KeystoreManager.getOrCreateDatabasePassphrase()
val supportFactory = SupportFactory(passphrase)

val secureDatabase = Room.databaseBuilder(context, AppDatabase::class.java, "secure_app.db")
    .openHelperFactory(supportFactory) // تشفير كامل للـ SQLite بـ AES-256 CBC
    .build()
```

## Why it matters and how it works

At rest, a key and authenticated encryption format protect stored content; Android file-based encryption already provides device-level protection, while app-level encryption may add protection for a specific threat model. In transit, TLS negotiates keys and validates the server certificate chain and hostname. Neither mode authorizes a payment.

## Worked example

For a banking app, use HTTPS with system certificate validation for API traffic, avoid cleartext exceptions, and store only minimal replaceable credentials locally. If app-level encryption is justified, keep its key in Keystore and define restore/key-loss behavior. Validate the backend response and user authorization separately.

## Trade-offs and decision criteria

App-level encryption adds complexity, key rotation and backup failures. Relying only on OS storage may be sufficient for non-sensitive cached data. Pinning is an optional additional network constraint with availability costs; it does not replace TLS validation.

## Failure modes

Disabling TLS validation for a test environment exposes all users if shipped. Backing up app-encrypted files without their device key makes them unreadable. Treat both as test cases: network interception should fail and restore should recover safely.

## Production perspective

Production reviews trace each sensitive field from collection through storage, transport, logs and deletion. Release builds reject cleartext traffic to sensitive endpoints, and telemetry records policy failures without recording secrets.

## Interview answer — short

Encryption at rest protects stored data on disk (via File-Based Encryption, SQLCipher, and Keystore). Encryption in transit protects network payloads traveling over the wire (via TLS 1.3, Network Security Config, and Certificate Pinning). Both protect data outside of active use, but plaintext inevitably resides in RAM while being processed.

## Interview answer — structured

A comprehensive defense-in-depth architecture secures data across both rest and transit states:

1. **Encryption in Transit (Over the Wire)**:
   - Guarantees confidentiality and integrity across public cellular and Wi-Fi networks.
   - Enforced via **TLS 1.2 / TLS 1.3** exclusively. Configured in Android via `res/xml/network_security_config.xml` with `cleartextTrafficPermitted="false"` to prevent accidental HTTP fallback.
   - Hardened with **Certificate Pinning** in OkHttp to defeat Man-in-the-Middle (MITM) interception from rogue CAs.

2. **Encryption at Rest (On Flash Storage)**:
   - **OS Level**: Modern Android uses **File-Based Encryption (FBE)**. User data is partitioned into Credential Encrypted (CE) storage, unlocked only after the user enters their lockscreen PIN/pattern.
   - **App Level**: Sensitive local databases are encrypted with **SQLCipher (AES-256)**, while tokens and keys are encrypted with **AES-GCM** using keys managed by `AndroidKeyStore`. If an attacker copies the SQLite file via ADB backup or file extraction, the file is unreadable binary ciphertext.

3. **Plaintext in Use**: Plaintext exists in application heap memory while being actively processed by the CPU, demanding careful buffer management and redaction in logging.

## Interview answer — deep senior

Differentiating Device-Encrypted (DE) vs. Credential-Encrypted (CE) Storage in FBE:

Starting in Android 7.0 (API 24), Android replaced Full-Disk Encryption (FDE) with File-Based Encryption (FBE):

- **CE Storage (`context.createCredentialProtectedStorageContext()`)**: The default storage for applications. Encrypted with a key derived from the user's lockscreen PIN and hardware Keystore. Unavailable after device reboot until the user enters their PIN for the first time (Direct Boot mode).

- **DE Storage (`context.createDeviceProtectedStorageContext()`)**: Encrypted with a key tied to the device hardware, available **before** the user unlocks the screen. Reserved strictly for components that must operate immediately after reboot before user unlock (alarm clocks, incoming call receivers, accessibility services).

Fintech and banking apps must never store financial records or auth tokens in DE storage; always retain credentials strictly in CE storage.

## How to answer in the interview

- **Why:** network and storage expose different attack windows.
- **How:** use validated TLS for transit and a justified local encryption design for stored data.
- **Trade-off:** local encryption creates key-loss and backup obligations.
- **Failure case:** plaintext leaks through logs or memory after decryption.
- **Production solution:** minimize retained data and test both network and restore paths.

## Deep-dive talking points

Separate on-disk ciphertext from TLS channel protection, identify who holds each key, and explain why neither replaces authenticated authorization.

## Follow-up questions

- **Interviewer:** "What is Direct Boot in Android?"
  **Answer:** "A mode where the device has booted up but the user has not yet entered their lockscreen PIN; only Device Protected (DE) storage is accessible."

- **Interviewer:** "Can an attacker read SQLCipher databases if they steal the phone while it's turned off?"
  **Answer:** "No. Without the device lockscreen PIN and Keystore hardware key derivation, SQLCipher ciphertext cannot be decrypted."

## Self-check rubric

Can I distinguish the two encryption windows, name plaintext exposure and backup limits, and keep authorization separate?

## References and reviewed-on date

- [Android Network Security Configuration](https://developer.android.com/privacy-and-security/security-config) — TLS/cleartext and trust settings.
- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore) — key protection.

Technically reviewed against primary documentation on 2026-10-13.
