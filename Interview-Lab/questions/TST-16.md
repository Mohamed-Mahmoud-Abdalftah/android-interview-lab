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

Test pure business rules, ViewModels, UseCases, mappers, and state machines on the local JVM for millisecond speed. Reserve on-device/emulator tests for framework and hardware boundaries: Android Keystore, BiometricPrompt, Room SQLite migrations, Macrobenchmark performance, and IPC components.

## Interview answer — structured

Allocating tests between the local JVM and real devices balances execution economics against operational fidelity.

First, **Local JVM Tests (`src/test/`) — The 80% Rule**. Next, with Scope, viewModels, pure domain UseCases, reactive StateFlow pipelines, business algorithms, DTO mappers, and state machines.
Additionally, a Why JVM executes in milliseconds. Zero emulator boot overhead. Allows rapid Test-Driven Development (TDD) iteration without blocking local machines. **On-Device / Emulator Tests (`src/androidTest/`) — The 20% Rule**.
With Hardware & Security Boundaries, Android Keystore hardware-backed keys, Secure Element operations, and `BiometricPrompt` flows (the JVM has no Keymaster TEE daemon). With Real SQLite Engine, Room database migrations and complex multi-threaded WAL transactions (desktop SQLite diverges from mobile OEM SQLite builds).
With Framework IPC, validating exported ContentProviders, BroadcastReceivers, and Deep Link intent filter matching. Finally, with Performance Profiling, baseline Profiles and Macrobenchmark measuring real frame rendering and startup latency.


## Interview answer — deep senior

From an engineering resource allocation and cloud cost perspective, minimizing on-device testing saves thousands of engineering hours.

First, with The Infrastructure Cost Calculation, 1,000 local unit tests execute in ~10 seconds on a standard GitHub Actions runner. 1,000 instrumented tests require spinning up dozens of nested-virtualization emulator containers, consuming 40+ minutes of cloud runner compute and thousands of dollars in monthly CI billing. Next, with Robolectric as the Middle Tier, where code requires light Android framework abstractions (e.g. `Bundle`, `Intent`, `Parcelable`, or `ColorRes`), use Robolectric on the JVM. This keeps tests in `src/test/` while providing simulated framework fidelity without emulator overhead.
Finally, with Architectural Separation as an Enabler, when architecture cleanly decouples domain logic into pure Kotlin modules (`:core:domain`), developers are physically prevented from importing Android framework classes, ensuring code remains 100% JVM testable by design.


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
