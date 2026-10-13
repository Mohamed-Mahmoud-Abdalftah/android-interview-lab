---
id: "SEC-15"
question: "How do you prevent token leakage through logs, screenshots, crash reports, and analytics?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 312
editorial_status: "reviewed"
---

# SEC-15

## Original interview question

How do you prevent token leakage through logs, screenshots, crash reports, and analytics?

## What the interviewer evaluates

- Multiple data-exfiltration channels beyond persistent storage.
- Redaction, screenshot policy and observability without token values.

## Explanation in Arabic

كيف تمنع تسريب الـ Tokens والبيانات الحساسة عبر الـ Logs، لقطات الشاشة (Screenshots)، تقارير الأعطال (Crash Reports)، وأدوات الـ Analytics؟

1. منع التسريب عبر الـ Logs (Logcat):
   - **قاعدة صارمة**: لا تطبع الـ Tokens أو كلمات المرور أو أرقام البطاقات في الـ Logcat أبداً.
   - في بيئة الـ Release، يجب تجريد استدعاءات `Log.d` و `Log.v` بالكامل عبر R8 (`-assumenosideeffects`).
   - يجب تخصيص `HttpLoggingInterceptor` في OkHttp بحيث يُستثنى هيدر `Authorization` والـ Cookies من الطباعة (`redactHeader("Authorization")`).

2. منع التسريب عبر لقطات الشاشة وقائمة الـ Recent Apps:
   - نظام أندرويد يأخذ لقطة شاشة تلقائية لواجهة التطبيق عند الضغط على زر Home أو فتح الـ App Switcher ويحفظها في ملفات النظام المؤقتة!
   - **الحل**: تفعيل `WindowManager.LayoutParams.FLAG_SECURE` على مستوى الـ Activity الحساسة. هذا يمنع تسجيل الشاشة، يمنع أخذ Screenshots، ويعرض شاشة سوداء أو فارغة في قائمة الـ Recent Apps.

3. منع التسريب عبر تقارير الأعطال (Crashlytics / Sentry):
   - عند حدوث Crash، قد يرسل SDK التقارير معلومات الـ State أو الشبكة. يجب فحص وتطهير (Sanitize) الـ Custom Keys وسجلات الأحداث عبر `beforeSend` Callback لحذف أي PII أو Bearer tokens.

4. منع التسريب عبر الـ Analytics:
   - يُمنع إرسال مدخلات المستخدم الصريحة أو مسارات الـ URLs الكاملة التي تحتوي على query parameters بها tokens إلى أدوات مثل Firebase Analytics أو Mixpanel.

## Practical walkthrough

تطبيق شامل لمنع تسريب البيانات الحساسة عبر الطبقات الأربع (Logs, Screen, Crashes, Network):
```kotlin
// 1. تأمين الشاشة ضد Screenshots والـ Recent Apps Switcher في Compose / Activity:
class SecurePaymentActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // يمنع تصوير الشاشة ويحمي واجهة التطبيق في قائمة المهام الأخيرة:
        window.setFlags(
            WindowManager.LayoutParams.FLAG_SECURE,
            WindowManager.LayoutParams.FLAG_SECURE
        )
        setContent { PaymentScreen() }
    }
}

// 2. تطهير هيدرز الشبكة ومنع تسريب الـ Tokens في Logcat:
fun createSecureLoggingInterceptor(): HttpLoggingInterceptor {
    return HttpLoggingInterceptor().apply {
        level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.HEADERS else HttpLoggingInterceptor.Level.NONE
        // إخفاء قيمة هيدر التفويض حتى في الـ Debug:
        redactHeader("Authorization")
        redactHeader("Cookie")
        redactHeader("X-Api-Key")
    }
}

// 3. تطهير تقارير Crashlytics قبل إرسالها:
class SecureCrashReporter {
    fun recordHandledException(throwable: Throwable) {
        // التحقق من خلو رسالة الخطأ من أي Bearer tokens قبل رفعها:
        val sanitizedMessage = throwable.message?.replace(Regex("Bearer\\s+[A-Za-z0-9\\-_.]+"), "Bearer [REDACTED]")
        FirebaseCrashlytics.getInstance().recordException(Exception(sanitizedMessage, throwable.cause))
    }
}
```

## Why it matters and how it works

Redaction is applied before data crosses an observability boundary, not only at dashboard display. Android `FLAG_SECURE` can prevent screenshots/recording for selected sensitive screens, but it has usability and platform limitations and cannot prevent all compromised-device capture. Crash SDKs and HTTP interceptors need separate configuration.

## Worked example

For sign-in troubleshooting, record `refresh_failed`, HTTP class, app version and an opaque request ID. Do not record the Authorization header, token prefix, password, raw request body or screenshot of account details. On a payment confirmation screen, evaluate `FLAG_SECURE` against product accessibility and support needs.

## Trade-offs and decision criteria

Allowlist telemetry reduces diagnostic detail, so add safe state transitions and correlation IDs. Screen capture blocking protects against some casual capture but can hinder support and still does not secure an instrumented process.

## Failure modes

Debug logging accidentally enabled in release can upload bearer tokens. A crash reporter may attach screenshots or custom attributes automatically. Audit SDK defaults, scan logs during tests, and revoke any credential found in telemetry.

## Production perspective

Use shared redaction at network and analytics boundaries, restrict dashboard access and retention, and test with synthetic secrets to ensure none reach collected events. Incident response includes secret rotation and affected-session revocation.

## Interview answer — short

Prevent leaks by masking Authorization headers via OkHttp's redactHeader, stripping Log calls in release builds with R8, setting FLAG_SECURE on sensitive Activities to block screenshots and recents snapshots, and sanitizing Crashlytics breadcrumbs and analytics events to strip PII and tokens before dispatch.

## Interview answer — structured

Data leakage occurs across four primary observation surfaces, each requiring deliberate architectural defenses:

1. **Logcat & Network Logs**: 
   - Configure OkHttp's `HttpLoggingInterceptor` using `redactHeader("Authorization")` and `redactHeader("Cookie")` to prevent printing tokens.
   - In release builds, use R8 rules (`-assumenosideeffects`) to strip `Log.d` and `Log.v` bytecodes entirely.

2. **Screen Capture & App Switcher (Task Snapshots)**:
   - When users background an app, Android saves a screenshot to disk for the multitasking overview. Applying `window.setFlags(WindowManager.LayoutParams.FLAG_SECURE, WindowManager.LayoutParams.FLAG_SECURE)` prevents screenshots, screen recording, and blacks out the task thumbnail in the recent apps switcher.

3. **Crash Reporting (Crashlytics/Sentry)**:
   - Scrub custom keys, breadcrumbs, and exception messages using filtering hooks (`beforeSend`). Network exception messages frequently contain full URLs with sensitive query parameters or authorization failure dumps.

4. **Analytics Pipelines**:
   - Enforce strict event data schemas. Never forward free-form user inputs, search queries with sensitive data, or complete server URLs to analytics tools.

## Interview answer — deep senior

From an operational compliance perspective (e.g. PCI-DSS, GDPR, HIPAA), unintentional token leakage is treated as a major security incident:

1. **Dynamic FLAG_SECURE Management**: In modern Jetpack Compose applications, `FLAG_SECURE` can be dynamically toggled using a `DisposableEffect` based on whether the currently visible composable displays sensitive data (e.g., credit card entry or seed phrases), rather than blindly applying it across the entire application which impairs legitimate UX like support screenshots.

2. **Memory Dumps & System Bug Reports**: When users trigger an Android bug report (`adb bugreport` or system developer settings), the OS dumps system log buffers and memory summaries. If tokens were printed to Logcat or stored in static string variables, they are bundled into plaintext bug report archives that users often share unencrypted over email or bug trackers.

3. **Automated CI Linting**: Integrate static analysis linters (e.g., custom Android Lint rules or Semgrep) in CI to fail PR builds if developers log sensitive parameter names (`token`, `password`, `pan`, `cvv`) or attach raw network responses to analytics events.

## How to answer in the interview

- **Why:** telemetry sinks create durable copies of secrets.
- **How:** allowlist safe fields before logging, disable body/header capture, and review crash/analytics sinks.
- **Trade-off:** less raw telemetry requires better correlation IDs.
- **Failure case:** a token enters a third-party SDK before redaction.
- **Production solution:** release-build leak tests and restricted access/retention.

## Deep-dive talking points

Audit redaction at HTTP logging, crash capture, analytics properties and screenshots; test release builds for accidental token exposure.

## Follow-up questions

- **Interviewer:** "Does FLAG_SECURE protect against root users capturing the screen via frame buffer reads?"
  **Answer:** "No; root users can read `/dev/graphics/fb0` or use SurfaceFlinger shell commands with root privileges to dump raw display hardware buffers."

- **Interviewer:** "Can OkHttp body logs leak JSON payloads containing passwords?"
  **Answer:** "Yes; if Level.BODY is enabled, request bodies are printed in plaintext. In production, logging should be set to Level.NONE or use custom redact interceptors."

## Self-check rubric

Can I enumerate leak channels, design an allowlist, test redaction and state incident response?

## References and reviewed-on date

- [Android sensitive data guidance](https://developer.android.com/privacy-and-security/security-best-practices) — handling sensitive information.
- [OWASP MASTG tests](https://mas.owasp.org/MASTG/tests/) — storage and log verification.

Technically reviewed against primary documentation on 2026-10-13.
