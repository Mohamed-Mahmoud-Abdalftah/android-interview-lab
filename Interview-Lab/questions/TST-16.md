---
id: "TST-16"
question: "What should be unit-tested versus verified with an emulator/device?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 411
editorial_status: "reviewed"
---

# TST-16

## Original interview question

What should be unit-tested versus verified with an emulator/device?

## What the interviewer evaluates

- JVM versus platform fidelity boundary.
- Emulator/device matrix driven by OS and hardware risks.

## Concept and technical explanation

Establishing a rigorous architectural boundary between local JVM unit testing and on-device instrumentation testing dictates the speed, fidelity, and operational cost of an Android engineering pipeline. Approximately 70 to 80 percent of application logic should be unit-tested purely on the host JVM in milliseconds without booting Android runtimes. This includes ViewModels, UseCases, business domain rules, mapping algorithms, offline caching logic using MockWebServer, and isolated Compose UI rendering via Robolectric. Conversely, on-device or emulator testing (comprising 15 to 20 percent) is strictly reserved for behaviors inextricably bound to the physical Android OS and ART runtime: complex SQLite Room database schema migrations, hardware biometric authentication via Android Keystore, native C++ NDK interop, WorkManager background constraints, CameraX hardware streams, and release-candidate macrobenchmarks.

## Practical walkthrough (English)

Contrasting local JVM domain testing with on-device biometric Keystore verification:
```kotlin
// 1. JVM Unit Test in src/test/ (Pure business validation executing in ~5ms)
class CartPricingUseCaseTest {
    @Test
    fun calculateTotal_appliesVatAndDiscountDeterministically() {
        val useCase = CalculateCartTotalUseCase()
        val total = useCase(items = listOf(CartItem(price = 100.0, qty = 2)), discount = 20.0)
        // 200 - 20 = 180 + 14% VAT = 205.2
        assertEquals(205.2, total, 0.001)
    }
}

// 2. Instrumented Test in src/androidTest/ (Strictly requires real Android Keystore hardware!)
@RunWith(AndroidJUnit4::class)
class CryptographyManagerIntegrationTest {
    private lateinit var cryptoManager: CryptographyManager

    @Before
    fun setup() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        cryptoManager = CryptographyManagerImpl(context)
    }

    @Test
    fun encryptAndDecryptToken_usingHardwareAndroidKeyStore() {
        val rawToken = "super_secret_jwt_token_payload"
        // Interacts with Android KeyStore provider inside hardware TEE / StrongBox!
        val encryptedData = cryptoManager.encrypt(alias = "auth_key", data = rawToken)
        val decryptedData = cryptoManager.decrypt(alias = "auth_key", encryptedData = encryptedData)

        assertEquals(rawToken, decryptedData)
    }
}
```

## Explanation in Arabic

ما هي المعايير الدقيقة لتحديد ما يجب اختباره كـ Unit Test على الـ JVM وما يجب التحقق منه على محاكي أو جهاز حقيقي (Emulator/Device)؟

1. المبدأ المعماري التوجيهي (The Golden Rule):
   - **اختبر على الـ JVM المحلي كل ما هو منطق برمجي بحت (Logic & State)**.
   - **اختبر على الجهاز الحقيقي كل ما يعتمد على عتاد الهاتف، نظام التشغيل، أو تعاريف النظام المنخفضة (Hardware, OS Drivers, Security)**.

2. ما يجب اختباره حصرياً كـ Unit Test على JVM (`src/test/`):
   - منطق الـ ViewModels وتدفقات الـ StateFlow والـ Events.
   - الـ UseCases وقواعد العمل وحسابات الأسعار والخصومات.
   - خوارزميات تحويل وتنسيق البيانات (Mappers & Adapters).
   - محاكاة أخطاء الـ API والـ Retries عبر MockWebServer.

3. ما يجب اختباره على جهاز حقيقي أو محاكي (`src/androidTest/`):
   - **العمليات التشفيرية العتادية (Android Keystore / StrongBox)**: الـ TEE والـ Hardware Keymaster غير موجودين على JVM!
   - **المصادقة البيومترية (BiometricPrompt)**: تتطلب عتاد مستشعر البصمة ونظام النظام.
   - **ترقيات قاعدة البيانات (Room Migrations)**: لاختبار محرك SQLite الحقيقي للأندرويد.
   - **الرسم المتقدم والـ Custom Views والأداء**: قياس الـ Frame Drops (JankStats) واختبارات الـ Macrobenchmark.
   - **مكونات الـ IPC والـ AndroidManifest**: مثل الـ ContentProviders و Deep Links والـ BroadcastReceivers.

## Practical walkthrough

المقارنة بين كود يختبر على الـ JVM وكود يستحيل اختباره إلا على جهاز حقيقي:
```kotlin
// 1. يختبر على الـ JVM في 5ms (منطق أعمال نقي - Domain Logic):
class LoanEligibilityCalculatorTest {
    @Test
    fun `eligible for loan when credit score above 700`() {
        val calculator = LoanEligibilityCalculator()
        val isEligible = calculator.evaluate(creditScore = 720, debtToIncomeRatio = 0.25)
        assertTrue(isEligible)
    }
}

// 2. يستحيل اختباره إلا على جهاز/محاكي حقيقي (تشفير عتادي بالـ Keystore):
@RunWith(AndroidJUnit4::class)
class HardwareKeystoreCryptoTest {
    @Test
    fun `keystore generates hardware key and encrypts payload`() {
        val cryptoManager = KeystoreCryptoManager()
        val secret = "ConfidentialToken123".toByteArray()
        
        val encrypted = cryptoManager.encrypt(secret)
        val decrypted = cryptoManager.decrypt(encrypted)
        
        // يعتمد على شريحة الـ Keymaster الحقيقية داخل الهاتف:
        assertEquals("ConfidentialToken123", String(decrypted))
    }
}
```

## Why it matters and how it works

JVM tests execute without Android runtime and cannot prove manifest, Binder, file backup or device UI behavior. I record which devices and SDK versions were actually covered. Some local Robolectric-style tests approximate framework behavior but are not a substitute for hardware or OS-specific validation.

## Worked example

Test a payment amount rounding function on JVM; test Room migration on emulator; test POS reader disconnect on actual terminal hardware with provider sandbox. A fake terminal callback test covers app state logic but not firmware timing.

## Trade-offs and decision criteria

Device tests cost time and infrastructure; prioritize platform-sensitive risks. JVM-only coverage is fast but can provide false assurance about security, process death and SDK behavior.

## Failure modes

A mocked permission manager test passes while the manifest lacks a permission. A simulated NFC SDK test passes while one ABI cannot load its `.so`. Use release-like device smoke tests for those boundaries.

## Production perspective

Build a supported API/device/ABI matrix. Run fast JVM PR checks, targeted emulator suites, and hardware release gates for payment-critical flows. Record which claims were device-verified.

## Interview answer — short

We divide testing strictly by execution environment. Fast JVM unit tests in src/test cover 70-80% of code: ViewModels, UseCases, business logic, mapping, and repositories with MockWebServer. Instrumented tests in src/androidTest cover 15-20% and are reserved strictly for platform-bound code: Room database migrations, Android Keystore encryption, hardware sensors, WorkManager system constraints, and release Macrobenchmarks that cannot execute accurately on the desktop JVM.

## Interview answer — structured

Striking the optimal balance between JVM unit tests and on-device emulator tests is the hallmark of a senior Android engineer.
The governing design principle is to run every test on the cheapest, fastest platform possible that still yields decisive confidence.
On the local JVM in src/test, we execute the vast majority of our test suite—roughly 70 to 80 percent.
Because JVM tests bypass Android OS boot cycles and run in milliseconds, they are ideal for testing domain UseCases, mathematical pricing logic, ViewModel state emissions with Turbine, data mapping, and repository network synchronization with MockWebServer.
Furthermore, using Robolectric or modern desktop Compose tooling, teams can even verify UI semantic layout and screenshot golden images directly on the JVM.
Conversely, on-device or emulator tests in src/androidTest are expensive, slow, and compute-intensive.
We reserve this tier strictly for functionality that directly interfaces with the compiled Android Runtime (ART) and native platform subsystems.
This includes verifying complex Room database migrations across historic SQLite versions, testing hardware biometric authentication backed by the Android Keystore and Secure Element, verifying background WorkManager scheduling under system battery-saver constraints, and executing Macrobenchmark startup and frame-timing metrics before production release.

## Interview answer — deep senior

Under the hood, the boundary between JVM and device testing is defined by runtime bytecode execution, native framework bridges, and hardware abstraction layers.
Local JVM tests compile against mockable-android.jar and run inside a desktop HotSpot or OpenJDK virtual machine.
Because desktop JVMs lack Android's native Linux zygote process, Binder IPC drivers, and hardware security modules, any attempt to test Android Keystore or SQLite file transactions requires either mocking or third-party shadows.
However, using shadows for complex hardware features introduces false confidence; Robolectric cannot replicate the exact cryptographic behavior of a hardware Trusted Execution Environment (TEE) or StrongBox keymaster.
Therefore, cryptographic key generation, biometric cipher initialization, and Room schema migrations must be validated inside the real Android Runtime (ART) via an emulator or physical device.
In src/androidTest, the test runner compiles code into Dalvik Executable (DEX) format and executes inside a real Linux process initialized by the Zygote daemon.
This guarantees genuine interaction with the Linux kernel, native C++ libsqlite3 engines, and hardware drivers.
Conversely, running pure business logic on an emulator wastes immense CI compute resources: booting an emulator takes minutes and running a suite takes ten times longer than on the JVM.
Senior engineers enforce an architectural firewall: if code contains pure business algorithms or presentation state transitions, it must be testable on the JVM via dependency injection; device execution is reserved strictly for platform integration validation.

## How to answer in the interview

- **Why:** a fake proves app policy but cannot emulate firmware or Android exactly.
- **How:** allocate rounding to JVM, lifecycle/Room to device and POS timing to hardware.
- **Trade-off:** speed and coverage versus cost of realistic environments.
- **Failure case:** a mocked disconnect is called terminal certification.
- **Production solution:** explicit device/provider coverage in release evidence.

## Deep-dive talking points

Prompt for JVM boundary, emulator API matrix, real hardware, release variant and claim scope.

## Follow-up questions

- **Interviewer:** "Can Android Keystore encryption be tested on a standard JVM unit test?"
  **Answer:** "No; AndroidKeyStore is an Android OS system provider coupled to hardware daemons (keystored/TEE), throwing NoSuchProviderException on a plain JVM."

- **Interviewer:** "Why should Macrobenchmark tests run only on physical devices or specialized emulators?"
  **Answer:** "Because standard emulators have artificial thermal and CPU profiles; Macrobenchmark requires real hardware to measure true user-perceived frame drops and cold start times."

## Self-check rubric

Place pure rounding/policy on JVM, Room or permission behavior on emulator, and reader disconnect timing on real hardware. Explain why a fake callback cannot certify firmware or platform integration.

## References and reviewed-on date

- [Android test fundamentals](https://developer.android.com/training/testing/fundamentals) — local versus instrumented tests.
- [Android device testing](https://developer.android.com/training/testing) — test environment guidance.

Technically reviewed against primary documentation on 2026-10-13.
