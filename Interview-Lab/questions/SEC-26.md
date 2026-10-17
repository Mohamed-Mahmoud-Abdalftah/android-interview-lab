---
id: "SEC-26"
question: "Design secure session storage for a fintech app on a potentially compromised device."
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "C"
phase: 3
priority: "P1"
order: 323
editorial_status: "reviewed"
---

# SEC-26

## Original interview question

Design secure session storage for a fintech app on a potentially compromised device.

## What the interviewer evaluates

- Session storage on a hostile endpoint with explicit residual risk.
- Token scope, refresh races, revocation and high-risk action step-up.

## Concept and technical explanation

Designing session storage under a hostile endpoint threat model requires zero trust in client integrity. The architecture isolates session state into ephemeral in-memory access tokens (valid for 5 to 15 minutes, never flushed to persistent disk) and hardware-bound refresh tokens encrypted via Android Keystore using AES-256-GCM. The refresh token is persisted in DataStore located inside noBackupFilesDir. High-risk financial operations enforce step-up authentication using biometric CryptoObject signing bound to KeyStore keys that require authentication per operation. In addition, token binding mechanisms like Demonstrating Proof-of-Possession (DPoP) tie tokens to an ephemeral client key pair, rendering exfiltrated tokens useless on external servers.

## Practical walkthrough (English)

Hostile-endpoint session storage with in-memory access token and hardware-bound refresh token:
```kotlin
class SecureSessionRepository(
    private val context: Context,
    private val keyStoreHelper: KeyStoreHelper
) {
    // 1. In-memory ephemeral access token; never written to persistent disk
    private val accessTokenRef = AtomicReference<String?>(null)
    private val refreshMutex = Mutex()

    fun getActiveAccessToken(): String? = accessTokenRef.get()

    fun updateAccessToken(token: String?) {
        accessTokenRef.set(token)
    }

    // 2. Hardware-encrypted refresh token stored strictly in noBackupFilesDir
    suspend fun saveRefreshToken(rawToken: String) = refreshMutex.withLock {
        val encryptedData = keyStoreHelper.encryptWithStrongBox(rawToken.toByteArray())
        val targetFile = File(context.noBackupFilesDir, "secure_session.enc")
        targetFile.writeBytes(encryptedData)
    }

    fun clearSession() {
        accessTokenRef.set(null)
        File(context.noBackupFilesDir, "secure_session.enc").delete()
    }
}
```

## Explanation in Arabic

كيف تصمم بنية تخزين الجلسات (Session Storage) لتطبيق بنكي (Fintech) يعمل على جهاز يُفترض أنه مخترق أو خاضع لسيطرة المهاجم؟

1. فرضية التهديد (Hostile Device Threat Model):
   - نفترض أن الجهاز معمول له Root، ويحتوي على أدوات مراقبة (Frida, Magisk)، ومساحة الذاكرة والقرص مكشوفة للمهاجم.
   - **الاستنتاج المعماري**: لا يمكن الاعتماد على أمان الهاتف بنسبة 100%؛ الأمان يجب أن ينبع من تقليص نافذة الخطر والتحقق السيرفري المشدد.

2. ركائز التصميم المعماري للجلسة الآمنة:
   - **Access Token قصير العمر في الـ RAM فقط**: مدة صلاحيته 5 دقائق. لا يُكتب على القرص أبداً لتقليص خطر استخراجه.
   - **Refresh Token مشفر عتادياً**: يُشفر بمفتاح AES-GCM من Android Keystore مدعوم بشريحة StrongBox/TEE. يُحفظ مشفراً في DataStore داخل مجلد `noBackupFilesDir`.
   - **العمليات المالية الحساسة محمية بـ CryptoObject بيومتري**: تحويل الأموال يتطلب توقيع المعاملة بمفتاح Keystore لا يفتح إلا ببصمة حية جديدة.
   - **Cryptographic Request Signing (DPoP / Asymmetric Signature)**: في كل طلب، يوقع التطبيق المعاملة بمفتاح خاص (Private Key) موجود في الـ Keystore. حتى لو سرق المهاجم الـ Token من الشبكة، لا يستطيع استخدامه بدون المفتاح الخاص المحبوس داخل عتاد الهاتف!
   - **Auto-Logout & Memory Purge**: عند وضع التطبيق في الخلفية لمدة دقيقتين، يتم مسح الـ Access Token ومصفوفات الذاكرة فوراً.

## Practical walkthrough

تصميم مستودع جلسة بنكية آمن مع إدارة الذاكرة والتشفير العتادي والمسح التلقائي عند الخلفية:
```kotlin
class SecureFintechSessionManager(
    private val keystoreStorage: KeystoreSecretStorage,
    private val sessionDataStore: DataStore<Preferences>
) : DefaultLifecycleObserver {
    // 1. الـ Access Token يعيش في الذاكرة فقط (RAM) ويُصفر برمجياً:
    @Volatile private var inMemoryAccessToken: String? = null
    private var backgroundTimestamp: Long = 0
    private val SESSION_TIMEOUT_MS = 2 * 60 * 1000L // دقيقتان كحد أقصى في الخلفية

    fun updateSession(accessToken: String, refreshToken: String) {
        inMemoryAccessToken = accessToken
        // 2. الـ Refresh Token يُشفر عتادياً بالـ Keystore ويُخزن في DataStore
        val encryptedRefresh = keystoreStorage.encrypt(refreshToken.toByteArray(Charsets.UTF_8))
        CoroutineScope(Dispatchers.IO).launch {
            sessionDataStore.edit { it[stringPreferencesKey("enc_refresh")] = Base64.encodeToString(encryptedRefresh, Base64.NO_WRAP) }
        }
    }

    override fun onStop(owner: LifecycleOwner) {
        backgroundTimestamp = System.currentTimeMillis()
    }

    override fun onStart(owner: LifecycleOwner) {
        if (backgroundTimestamp > 0 && (System.currentTimeMillis() - backgroundTimestamp) > SESSION_TIMEOUT_MS) {
            // 3. انتهاء مدة الجلسة؛ مسح الذاكرة وتوجيه المستخدم لتسجيل الدخول
            purgeSessionMemory()
        }
    }

    fun purgeSessionMemory() {
        inMemoryAccessToken = null
        backgroundTimestamp = 0
    }
}
```

## Why it matters and how it works

Keystore raises extraction cost for a local wrapping key, but hooks can observe tokens when decrypted or sent. The server owns grant validity and can bind risk signals to a session, enforce limits and revoke it. Refresh must be single-flight in one process and tolerate unknown network outcomes without resurrecting old sessions.

## Worked example

A transfer app stores a replaceable refresh token in app-private, encrypted storage and keeps access tokens in memory. On launch it refreshes under a session-generation lock; if the key is unavailable it asks for login. For a large transfer it gets fresh server challenge/step-up, not a local “biometric passed” Boolean.

## Trade-offs and decision criteria

Durable sessions improve usability but extend exposure. Hardware-backed protection, if available, may help against offline extraction, not runtime compromise. Stronger step-up adds friction; use risk tiers and accessible recovery.

## Failure modes

An attacker hooks token-read code and captures a bearer token despite encryption. An old refresh response arrives after logout and restores the session. Enforce server revocation and compare session generation before committing any refresh result.

## Production perspective

Monitor session anomalies, provide per-device revocation, minimize scopes, and test rooted/hooked devices, backup restore and process death. Never log token values. Payment state is independently reconciled by the backend.

## Interview answer — short

Designing secure session storage on an untrusted device requires assuming the client is hostile. We keep short-lived access tokens exclusively in memory, never writing them to disk. The long-lived refresh token is encrypted using hardware-backed Android Keystore keys via StrongBox and stored in noBackupFilesDir. Critical transactions require biometric signing step-up, and tokens are bound using proof-of-possession.

## Interview answer — structured

Securing session storage on a potentially compromised device begins with a zero-trust model where local disk and memory are assumed accessible to an attacker.
We separate session credentials into two tiers with distinct lifecycles and storage rules.
The access token is strictly ephemeral, valid for five to fifteen minutes, and kept solely in volatile application memory as a mutable reference that is zeroed upon logout or app suspension.
It is never written to SharedPreferences, SQLite, or cache files.
The refresh token, which is long-lived, is stored in encrypted DataStore inside the noBackupFilesDir directory, protected by an AES-256-GCM key bound to Android Keystore and hardware StrongBox.
To prevent token exfiltration from granting unlimited access, the backend issues cryptographically bound tokens using Demonstrating Proof-of-Possession.
High-value financial actions enforce step-up authentication using a biometric CryptoObject, requiring an authenticated hardware key signature per transaction.
Token refresh logic coordinates through a concurrency mutex to prevent race conditions during network handoffs.

## Interview answer — deep senior

In mobile fintech threat modeling, we treat the client device as an untrusted environment where root access, runtime instrumentation like Frida, and offline backup extraction are active probabilities.
Our session architecture establishes defense in depth across memory, storage, and transport boundaries.
In memory, the access token resides inside a thread-safe atomic reference, completely bypassing persistent disk writes.
When the application moves to the background for longer than our security timeout, we wipe this reference deterministically.
For persistence, the refresh token is encrypted through EncryptedSharedPreferences or Proto DataStore utilizing an Android Keystore master key generated with StrongBox backing.
The storage location is explicitly isolated within noBackupFilesDir, preventing ADB backups or cloud synchronization from lifting the encrypted payload to unmanaged secondary devices.
At the cryptographic protocol layer, we bind tokens to an ephemeral device key pair using DPoP, ensuring that even if an attacker extracts the refresh token via a memory dump, replay attempts from another IP or client will fail backend verification.
Furthermore, routine session tokens cannot authorize sensitive financial operations.
Any fund transfer requires a stepped-up transaction payload signed by a dedicated EC key requiring BiometricPrompt authorization with zero timeout.
This ensures that compromised session tokens cannot trigger irreversible fund movements without live biometric confirmation. In addition, we invalidate cached session state immediately upon user logout or network disconnection, wiping sensitive memory buffers completely.

## How to answer in the interview

- **Why:** a compromised device can inspect credentials during use.
- **How:** minimize token lifetime, protect necessary persistence, and authorize sensitive operations server-side.
- **Trade-off:** tighter session policy adds user friction.
- **Failure case:** relying on Keystore to prevent runtime token theft.
- **Production solution:** refresh rotation, revocation, step-up, and anomaly limits.

## Deep-dive talking points

Prompt for four threat classes, session-generation race, key-loss recovery, server revocation and step-up limits.

## Follow-up questions

- **Interviewer:** "What is DPoP and how does it prevent token replay?"
  **Answer:** "DPoP (Demonstrating Proof-of-Possession) binds access tokens to a client's private key; each request includes a JWT signed by that key, making stolen tokens non-reusable without the hardware private key."

- **Interviewer:** "Why should session tokens never be stored in static variables across Application subclasses?"
  **Answer:** "Static references persist across Activity lifecycles without automatic garbage collection, extending the attack window for heap inspection."

## Self-check rubric

Can I describe storage, runtime residual risk, refresh/logout races and server authorization?

## References and reviewed-on date

- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore) — local key limits.
- [Play Integrity overview](https://developer.android.com/google/play/integrity/overview) — risk signals.

Technically reviewed against primary documentation on 2026-10-13.
