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

## Concept and technical explanation

Encryption at rest and encryption in transit are the two complementary pillars of end-to-end data confidentiality on Android, protecting sensitive information across distinct operational states. Encryption at rest secures persistent data stored on non-volatile physical flash storage against offline extraction, device theft, and unauthorized access. Modern Android implements this at the system level via File-Based Encryption (FBE), partitioning storage into Credential Encrypted (CE) storage (accessible only after the user unlocks the device with their PIN or biometrics) and Device Encrypted (DE) storage (accessible during Direct Boot before unlock for critical services like alarms). At the application level, developers layer additional cryptographic security using the Jetpack Security library (EncryptedSharedPreferences and EncryptedFile) or SQLCipher for encrypted Room databases, binding encryption keys to the Android Keystore. Encryption in transit protects data moving across volatile public and private networks between the mobile client and remote backend services against eavesdropping, interception, and man-in-the-middle (MITM) tampering. It relies on Transport Layer Security (TLS 1.3), robust cipher suites, and Android Network Security Configuration.

## Practical walkthrough (English)

Implementing layered encryption at rest and encryption in transit in Android:
```kotlin
// 1. Encryption at rest: EncryptedSharedPreferences backed by hardware Keystore
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val securePreferences = EncryptedSharedPreferences.create(
    context,
    "user_pii_vault",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

// 2. Encryption in transit: Strict TLS 1.3 enforcement via OkHttpClient
val secureHttpClient = OkHttpClient.Builder()
    .connectionSpecs(listOf(
        ConnectionSpec.MODERN_TLS // Enforces TLS 1.2 and TLS 1.3 with secure cipher suites
    ))
    .certificatePinner(
        CertificatePinner.Builder()
            .add("api.bank.com", "sha256/k2oTQLj4nsdKmSOGKEUbhwEYfEuDYV5R6g28AzERdOk=")
            .build()
    )
    .build()
```

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

Encryption at rest secures data stored on the device's physical disk using File-Based Encryption, EncryptedSharedPreferences, or SQLCipher so stolen or dumped storage remains unreadable. Encryption in transit protects data travelling over the network using TLS 1.3 and certificate pinning, preventing eavesdropping and man-in-the-middle tampering during transmission.

## Interview answer — structured

Comprehensive mobile confidentiality demands securing data both when it resides persistently on device hardware and while it traverses network pathways.
Encryption at rest protects stored bytes against offline extraction, forensic dumping, and device theft.
At the operating system level, Android employs File-Based Encryption with two cryptographic zones: Device Encrypted storage available during Direct Boot before user unlock, and Credential Encrypted storage unlocked only when the user enters their lockscreen credentials.
Within the application, developers protect sensitive records using EncryptedSharedPreferences for key-value pairs and SQLCipher for Room databases, anchoring symmetric encryption keys directly in the hardware-backed Android Keystore.
Encryption in transit protects data packets moving over public cellular and Wi-Fi networks against interception, tampering, and eavesdropping.
This is implemented using modern Transport Layer Security protocols, specifically TLS 1.2 and TLS 1.3, which negotiate authenticated key exchange and symmetric payload ciphers.
To harden transit security against compromised certificate authorities and rogue corporate proxies, applications configure Android Network Security Configuration to disallow cleartext traffic and implement public key certificate pinning.

## Interview answer — deep senior

When analyzing threat models for enterprise and financial applications, understanding the precise boundary where encryption at rest ends and encryption in transit begins is essential for operational security.
A common failure mode is assuming that because Android provides platform-level File-Based Encryption, application-level encryption is unnecessary.
While FBE protects physical flash partitions if a powered-off device is stolen, once the user unlocks their phone, the Credential Encrypted partition is mounted and decrypted in the Linux kernel.
If an attacker exploits a local vulnerability or gains privileged execution in an adjacent process, raw files in the application sandbox become accessible unless protected by an application-level layer such as Jetpack Security or SQLCipher backed by Keystore master keys.
Conversely, encryption in transit guarantees that packets flowing between the client socket and the cloud load balancer remain confidential and tamper-proof.
However, transport encryption terminates at the network endpoint.
If an application transmits sensitive payloads over HTTPS without certificate pinning, a user on a managed enterprise network with an installed root CA certificate or an attacker using a rogue cellular base station can execute a Man-in-the-Middle attack.
Therefore, a defense-in-depth architecture enforces TLS 1.3 with Certificate Pinning for transit, uses EncryptedSharedPreferences backed by hardware Keystore keys for local data at rest, and rigorously zeroes out sensitive memory buffers so credentials are protected even while resident in RAM.

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
