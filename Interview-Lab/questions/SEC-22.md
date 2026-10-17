---
id: "SEC-22"
question: "How do you design biometric-gated access to a Keystore operation?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 319
editorial_status: "reviewed"
---

# SEC-22

## Original interview question

How do you design biometric-gated access to a Keystore operation?

## What the interviewer evaluates

- Authentication prompt, Keystore key authorization and Cipher binding.
- Biometric enrollment/credential fallback and key invalidation limits.

## Concept and technical explanation

Designing biometric-gated access to an Android Keystore cryptographic operation establishes a hardware-enforced bond between physical human biometric verification and mathematical cipher execution. Rather than treating biometric prompts as mere UI authorization gates, the cryptographic key itself must be configured to be mathematically unusable without prior biometric unlock. The key is generated in AndroidKeyStore using KeyGenParameterSpec configured with setUserAuthenticationRequired(true) and setUserAuthenticationParameters(0, KeyProperties.AUTH_BIOMETRIC_STRONG), requiring Class 3 (Strong) biometrics per-operation. When initiating an operation, the application initializes a Cipher or Signature object with the Keystore key. Because the key is locked, executing cipher operations immediately throws a UserNotAuthenticatedException. Instead, the initialized Cipher is wrapped inside a BiometricPrompt.CryptoObject and passed to BiometricPrompt.authenticate(). Only upon successful hardware biometric verification does the framework unlock the Keymaster key, returning the authenticated CryptoObject to onAuthenticationSucceeded, where cipher.doFinal() can finally execute.

## Practical walkthrough (English)

Implementing BiometricPrompt with cryptographic Keystore binding:
```kotlin
class BiometricCryptoManager(private val activity: FragmentActivity) {
    private val keyAlias = "biometric_payment_key"

    // 1. Generate key requiring strong biometrics per operation (timeout = 0)
    fun generateBiometricKey() {
        val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        val spec = KeyGenParameterSpec.Builder(
            keyAlias,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        ).run {
            setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            setUserAuthenticationRequired(true) // Hardware lock
            setUserAuthenticationParameters(0, KeyProperties.AUTH_BIOMETRIC_STRONG) // Per-use
            setInvalidatedByBiometricEnrollment(true) // Invalidate if new fingerprint added
            build()
        }
        keyGenerator.init(spec)
        keyGenerator.generateKey()
    }

    // 2. Authenticate and execute cipher bound to BiometricPrompt.CryptoObject
    fun authenticateAndDecrypt(encryptedData: ByteArray, iv: ByteArray, onSuccess: (ByteArray) -> Unit) {
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        val secretKey = keyStore.getKey(keyAlias, null) as SecretKey
        
        val cipher = Cipher.getInstance("AES/GCM/NoPadding").apply {
            init(Cipher.DECRYPT_MODE, secretKey, GCMParameterSpec(128, iv))
        }

        val cryptoObject = BiometricPrompt.CryptoObject(cipher)
        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Confirm Payment")
            .setSubtitle("Authenticate using biometrics to unlock your key")
            .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
            .setNegativeButtonText("Cancel")
            .build()

        val biometricPrompt = BiometricPrompt(activity, ContextCompat.getMainExecutor(activity),
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    // Authenticated Cipher is now hardware-unlocked and ready for doFinal!
                    val authenticatedCipher = result.cryptoObject?.cipher
                    val plaintext = authenticatedCipher?.doFinal(encryptedData)
                    plaintext?.let(onSuccess)
                }
            })

        biometricPrompt.authenticate(promptInfo, cryptoObject)
    }
}
```

## Explanation in Arabic

كيف تصمم وصولاً مشروطاً بالبصمة (Biometric-Gated Access) لعمليات Android Keystore بشكل عتادي لا يمكن تجاوزه برمجياً؟

1. الفرق الجوهري بين الفحص الشكلي والتأمين العتادي:
   - **الفحص الشكلي (Boolean Authentication - ❌)**: مجرد إظهار `BiometricPrompt` واستدعاء العملية في `onAuthenticationSucceeded()`. هذا الفحص يمكن لمهاجم تجاوزه بسطر واحد في Frida عبر استدعاء الـ Callback مباشرة دون لمس مستشعر البصمة!
   - **التأمين العتادي التشفيري (Crypto-Gated Authentication - ✅)**: ربط مفتاح الـ Keystore بمتطلب التحقق البيومتري (`setUserAuthenticationRequired(true)`). في هذا النمط، يظل المفتاح مقفلاً داخل عتاد الهاتف (TEE / Secure Element) وترفض الشريحة إجراء أي عملية تشفير أو فك تشفير حتى يقدم مستشعر البصمة العتادي تصريحاً مشفراً للـ Keystore!

2. دور كائن `BiometricPrompt.CryptoObject`:
   - نقوم بإنشاء `Cipher` غير مهيأ بالكامل، ونمرره مغلفاً داخل `CryptoObject` إلى `BiometricPrompt.authenticate()`.
   - عند نجاح البصمة الحقيقية عتادياً، يفتح الـ Keymaster تصريح الـ Cipher مؤقتاً.
   - نقوم باسترجاع الـ Cipher المشفر من الـ Callback واستخدامه في تنفيذ `cipher.doFinal()`. لو حاول المهاجم استدعاء الـ Callback عبر Frida دون بصمة حقيقية، سيفشل `cipher.doFinal()` برمي `UserNotAuthenticatedException` لأن العتاد لم يفتح المفتاح!

## Practical walkthrough

تنفيذ Biometric-Gated Crypto حقيقي مدعوم عتادياً ومحصن ضد هجمات الـ Hooking:
```kotlin
class BiometricCryptoManager(private val activity: FragmentActivity) {
    private val KEY_ALIAS = "biometric_user_vault_key"

    // 1. توليد مفتاح مقفل عتادياً يتطلب بصمة المستخدم لكل عملية:
    fun generateBiometricProtectedKey() {
        val keyGen = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        val spec = KeyGenParameterSpec.Builder(
            KEY_ALIAS,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setUserAuthenticationRequired(true) // يتطلب بصمة لكل عملية تشفير/فك تشفير
            .setUserAuthenticationParameters(0, KeyProperties.AUTH_BIOMETRIC_STRONG) // مدة الصلاحية 0 = لكل عملية على حدة
            .setInvalidatedByBiometricEnrollment(true) // إبطال المفتاح فوراً إذا أضيفت بصمة جديدة للهاتف
            .build()
        keyGen.init(spec)
        keyGen.generateKey()
    }

    // 2. فك تشفير البيانات عبر ربط الـ Cipher بـ BiometricPrompt.CryptoObject:
    fun authenticateAndDecrypt(iv: ByteArray, ciphertext: ByteArray, onSuccess: (ByteArray) -> Unit) {
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        val secretKey = keyStore.getKey(KEY_ALIAS, null) as SecretKey
        val cipher = Cipher.getInstance("AES/GCM/NoPadding").apply {
            init(Cipher.DECRYPT_MODE, secretKey, GCMParameterSpec(128, iv))
        }

        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Confirm payment")
            .setNegativeButtonText("Cancel")
            .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
            .build()

        val biometricPrompt = BiometricPrompt(
            activity,
            ContextCompat.getMainExecutor(activity),
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    // الـ Cipher الآن فقط أصبح مفكوك القفل عتادياً!
                    val authenticatedCipher = result.cryptoObject?.cipher!!
                    val decryptedPayload = authenticatedCipher.doFinal(ciphertext)
                    onSuccess(decryptedPayload)
                }
            }
        )

        // تمرير الـ CryptoObject إلزامي لجعل القفل عتادياً
        biometricPrompt.authenticate(promptInfo, BiometricPrompt.CryptoObject(cipher))
    }
}
```

## Why it matters and how it works

A KeyGenParameterSpec may require user authentication for key use. For an auth-per-use key, initialize a Cipher and pass it as a CryptoObject to BiometricPrompt; only after a successful result perform the operation. API and authenticator combinations vary across versions, so verify supported combinations for the app’s minimum API and AndroidX Biometric version.

## Worked example

A high-value local signing step creates a Keystore signing key requiring per-use strong authentication. The app signs a server challenge after BiometricPrompt succeeds. The server verifies the signature and still checks the current session and transfer details. The signature is evidence of key use, not user intent by itself.

## Trade-offs and decision criteria

Per-use authentication raises friction but better binds operation to a fresh gesture. Time-window authentication improves convenience but widens the period of permitted use. Device credential fallback and enrollment changes affect recovery and must be tested.

## Failure modes

Calling BiometricPrompt then reading a plaintext token from preferences leaves the token independent of the prompt. An auth-bound key can become invalid, so provide a safe sign-in/re-enrollment path rather than silently bypassing the gate.

## Production perspective

For a fintech flow, threat-model which exact operation needs a gesture; use a server challenge tied to operation ID and amount, a Keystore key with appropriate user-auth policy, and audit without biometric data. Test enrollment change, cancel, lockout and process death.

## Interview answer — short

We design biometric access by generating a Keystore key configured with setUserAuthenticationRequired, making the key mathematically unusable without hardware biometric authentication. We initialize a Cipher, wrap it in a BiometricPrompt.CryptoObject, and authenticate; only upon successful biometric verification does the hardware unlock the key to finalize encryption or signing.

## Interview answer — structured

Biometric-gated security in Android requires binding cryptographic execution directly to biometric verification rather than relying on decoupled UI dialogs.
A common security flaw is displaying BiometricPrompt as a UI gate, and upon success, reading an unencrypted token from SharedPreferences; an attacker using Frida easily hooks the callback to bypass the prompt.
To build true hardware-backed protection, the cryptographic key must be locked at the Keystore level.
We generate a key using KeyGenParameterSpec, enabling setUserAuthenticationRequired and specifying a zero-second duration with Class 3 Strong biometrics.
This configuration ensures that the key cannot perform cryptographic operations without an active biometric authentication ticket issued by the secure hardware.
During execution, we initialize our Cipher or Signature object and wrap it inside a BiometricPrompt.CryptoObject.
We pass the CryptoObject to BiometricPrompt.authenticate.
When the user successfully authenticates with their fingerprint or face, the Keymaster daemon receives the hardware auth token and unlocks the key, allowing onAuthenticationSucceeded to execute doFinal on the authenticated Cipher securely.

## Interview answer — deep senior

The critical security distinction in biometric engineering is the separation between UI-level authentication and cryptographic key unlocking.
If an application invokes BiometricPrompt without passing a CryptoObject, the biometric ceremony is purely advisory: the framework executes a local biometric check and returns a Boolean result to the application process.
In a threat model where an attacker possesses a rooted device or uses runtime hooking platforms like Frida, hooking AuthenticationCallback.onAuthenticationSucceeded() to fabricate a successful result requires trivial effort.
By contrast, integrating BiometricPrompt.CryptoObject creates a hardware-rooted cryptographic barrier.
When a key is generated with setUserAuthenticationRequired(true) and setUserAuthenticationParameters(0, AUTH_BIOMETRIC_STRONG), the key material resides inside the TEE or StrongBox in a locked state.
Initializing the Cipher allocates an operation handle in Keymaster, but calling doFinal() prior to biometric verification fails with UserNotAuthenticatedException.
When the user authenticates, the biometric sensor (Fingerprint or Face HAL) communicates directly with the Gatekeeper and Keymaster secure daemons via hardware channels, issuing a cryptographically signed authentication ticket containing a timestamp and HMAC.
Keymaster validates this hardware ticket and authorizes the specific cipher operation handle.
Only then does doFinal() succeed inside onAuthenticationSucceeded().
Furthermore, setting setInvalidatedByBiometricEnrollment(true) guarantees that if an unauthorized individual adds a new fingerprint to the device in system settings, the key is permanently destroyed, providing absolute non-repudiation for high-value banking transactions.

## How to answer in the interview

- **Why:** a biometric dialog alone is a UI gate.
- **How:** bind an auth-required Keystore key operation to CryptoObject and sign a fresh server challenge.
- **Trade-off:** authenticator/device support affects UX and key policy.
- **Failure case:** a bypassed callback authorizes money.
- **Production solution:** server challenge binding and documented recovery when biometric enrollment invalidates keys.

## Deep-dive talking points

Prompt for auth-bound key, CryptoObject, per-use versus time-window policy, enrollment invalidation and server challenge binding.

## Follow-up questions

- **Interviewer:** "Can Face Unlock on budget Android devices unlock AUTH_BIOMETRIC_STRONG keys?"
  **Answer:** "No; standard 2D camera face recognition is classified as Class 1 or Class 2 (Weak) and Android Keystore blocks it from unlocking Strong-tier cryptographic keys."

- **Interviewer:** "What happens if the device has no screen lock set when generating a biometric key?"
  **Answer:** "KeyGenParameterSpec initialization fails immediately with an InvalidAlgorithmParameterException because secure lock screen credentials are a prerequisite."

## Self-check rubric

Can I distinguish UI gating from cryptographic gating and describe operation-bound verification?

## References and reviewed-on date

- [BiometricPrompt guide](https://developer.android.com/identity/sign-in/biometric-auth) — cryptographic authentication flow.
- [KeyGenParameterSpec](https://developer.android.com/reference/android/security/keystore/KeyGenParameterSpec) — user-auth key constraints.

Technically reviewed against primary documentation on 2026-10-13.
