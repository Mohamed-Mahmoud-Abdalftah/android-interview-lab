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

Gate Keystore operations with biometrics by setting setUserAuthenticationRequired(true) on the key and passing a Cipher wrapped in a BiometricPrompt.CryptoObject to authenticate(). Decrypt only using the authenticated Cipher in onAuthenticationSucceeded; hardware enforces key release, preventing bypass via software hooks.

## Interview answer — structured

Biometric-gated security must be backed cryptographically rather than relying on boolean UI callback results:

1. **The Vulnerability of Boolean Prompts**: Invoking `BiometricPrompt.authenticate(promptInfo)` without a `CryptoObject` treats the result as a simple boolean status. An attacker running Frida hooks `onAuthenticationSucceeded()` to invoke the success callback directly without touching the sensor.

2. **Hardware Cryptographic Binding (CryptoObject)**:
   - When generating the AES key in `AndroidKeyStore`, configure `.setUserAuthenticationRequired(true)` with `.setUserAuthenticationParameters(0, AUTH_BIOMETRIC_STRONG)` and `.setInvalidatedByBiometricEnrollment(true)`.
   - Initialize a `Cipher` with the key and wrap it inside `BiometricPrompt.CryptoObject(cipher)`.
   - Pass the `CryptoObject` into `biometricPrompt.authenticate()`.

3. **Hardware Enforcement**: The Android Keymaster / TEE hardware keeps the key material locked. Only upon receiving authenticated biometric proof from the hardware fingerprint sensor does the secure enclave release the cryptographic key for that specific `Cipher` instance. Attempting to call `cipher.doFinal()` without biometric hardware unlocking throws `UserNotAuthenticatedException`.

## Interview answer — deep senior

From an architectural standpoint, designing biometric crypto requires handling edge cases in the user security lifecycle:

1. **Biometric Enrollment Changes**: When a user registers a new finger on the device, `setInvalidatedByBiometricEnrollment(true)` immediately renders the key permanently unusable. Any subsequent `cipher.init()` throws `KeyPermanentlyInvalidatedException`. The application must handle this by safely deleting the invalid key, purging local biometric-gated caches, and prompting the user for full password authentication.

2. **Per-Use vs. Time-Window Authentication**: Specifying a duration of `0` in `setUserAuthenticationParameters` requires biometric verification for every individual cryptographic transaction. Setting a duration greater than zero allows the hardware key to remain unlocked for that duration (e.g., 30 seconds), which is useful for bulk operations but presents a larger attack window.

3. **Strong vs. Weak Biometrics**: Financial applications must strictly configure `BiometricManager.Authenticators.BIOMETRIC_STRONG` (Class 3 hardware with < 0.002% False Acceptance Rate and liveness detection). Weak biometrics (Class 2 / 2D camera face unlock) are prohibited from unlocking Keystore keys marked with `AUTH_BIOMETRIC_STRONG`.

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
