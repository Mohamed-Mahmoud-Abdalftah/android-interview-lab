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

Design secure session storage on hostile devices by keeping short-lived access tokens strictly in RAM, storing refresh tokens encrypted via Android Keystore AES-GCM in noBackupFilesDir, signing requests with hardware-bound asymmetric keys (DPoP), and deterministically zeroing in-memory tokens upon a 2-minute background timeout.

## Interview answer — structured

Designing fintech session storage on potentially compromised devices assumes a zero-trust posture toward the client OS:

1. **In-Memory Short-Lived Access Tokens**: Retain access tokens exclusively in volatile RAM with brief 5-minute lifetimes. Never persist access tokens to disk. If the process is killed or backgrounded past timeout, the token vanishes naturally.

2. **Hardware-Bound Refresh Token Storage**: Persist the long-lived refresh token encrypted with a 256-bit AES-GCM key backed by Android Keystore and StrongBox Keymaster. Store the ciphertext inside `context.noBackupFilesDir` to prevent extraction via adb or cloud backups.

3. **Demonstrating Proof-of-Possession (DPoP)**: Bind the session to an asymmetric EC keypair generated inside Keystore. For critical API calls, the client signs a payload containing the current timestamp, request URI, and server nonce with the hardware-locked private key. Intercepting the bearer token alone is useless to an attacker because they cannot forge the hardware signature.

4. **Lifecycle-Aware Background Eviction**: Monitor app foreground/background lifecycle. After 120 seconds in the background, aggressively purge all memory pointers and cached session states, forcing biometric or passcode re-authentication on resume.

## Interview answer — deep senior

From an end-to-end security architecture viewpoint, fintech resilience depends on continuous risk telemetry and backend orchestration:

1. **Server-Side Session Invalidation**: The server maintains a distributed state table tracking device fingerprint hashes, IP geographic velocity, and integrity verdicts. If a refresh request originates from an anomalous ASN or fails Play Integrity attestation, the server immediately revokes the token family and pushes a silent FCM wake-up to terminate the local session.

2. **Step-Up Authentication Gates**: High-value transactions (e.g. transfers over $1,000) are never authorized solely by existing session tokens. They require just-in-time biometric unlocking using a `CryptoObject`-bound Keystore key paired with a server-issued one-time transaction nonce.

3. **Anti-Screen-Scraping**: The host Activity enforces `FLAG_SECURE` to prevent accessibility-based overlays, screen recording, and task preview dumping from capturing session states while the app is transitioning.

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
