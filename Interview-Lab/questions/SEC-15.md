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

## Concept and technical explanation

Securing authentication credentials and personally identifiable information (PII) on Android requires defending against passive exfiltration channels that bypass encrypted disk storage. These unintended leakage vectors primarily include application logging frameworks, operating system task snapshot previews, third-party crash reporting SDKs, and behavioral analytics pipelines. System logs (Logcat) can be intercepted on older platforms or inspected via debugging tools; production builds must strip debug logs completely using R8 ProGuard rules (-assumenosideeffects) or custom Timber tree filters. Task switcher snapshots and screen recording present a physical and software shoulder-surfing vulnerability, mitigated by setting WindowManager.LayoutParams.FLAG_SECURE on sensitive activity windows. Crash reporting services (such as Firebase Crashlytics or Sentry) frequently record network traces, custom keys, or exception messages containing raw authorization headers unless intercepted by strict redaction filters. Similarly, product analytics SDKs (such as Firebase Analytics or Mixpanel) must enforce automated sanitization rules preventing tokens, passwords, or credit card numbers from entering event parameter bundles.

## Practical walkthrough (English)

Securing window previews, network logging, and crash report data exfiltration:
```kotlin
// 1. Prevent screenshots, screen recording, and task switcher previews
class SensitivePaymentActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Blanks out screen preview in Android Recents overview and blocks screenshots
        window.setFlags(
            WindowManager.LayoutParams.FLAG_SECURE,
            WindowManager.LayoutParams.FLAG_SECURE
        )
    }
}

// 2. Redacting sensitive Authorization headers in OkHttp network logging
val loggingInterceptor = HttpLoggingInterceptor().apply {
    level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BODY else HttpLoggingInterceptor.Level.NONE
    redactHeader("Authorization")
    redactHeader("Proxy-Authorization")
    redactHeader("Cookie")
    redactHeader("Set-Cookie")
}

// 3. Sanitizing Crashlytics custom crash keys to strip PII and tokens
fun recordSafeCrashBreadcrumb(key: String, value: String) {
    val sanitizedValue = if (key.contains("token", ignoreCase = true) || key.contains("auth", ignoreCase = true)) {
        "[REDACTED]"
    } else {
        value
    }
    FirebaseCrashlytics.getInstance().setCustomKey(key, sanitizedValue)
}
```

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

We prevent token leakage across side-channels by stripping debug logs via R8 in release builds, setting FLAG_SECURE on sensitive windows to block screenshots and task snapshots, redacting Authorization headers in network interceptors, and sanitizing error payloads and analytics events before sending them to third-party crash trackers.

## Interview answer — structured

Eliminating credential leakage requires securing the side-channels through which sensitive data accidentally escapes application boundaries.
The first vector is system logging; in release configurations, we configure R8 rules to remove Logcat invocations entirely and employ Timber trees that discard debug messages.
The second vector is screen capture and recent task previews.
By applying WindowManager FLAG_SECURE to our activity windows, the Android system blocks screenshots, screen recording, and renders a blank preview card in the task switcher, protecting sensitive financial data from shoulder-surfing.
The third vector is third-party crash reporting and observability SDKs like Crashlytics and Sentry.
We implement custom exception filters that sanitize stack traces and redacting interceptors in OkHttp that scrub Authorization and Cookie headers before network logs are generated.
Finally, we enforce strict payload sanitization policies in our analytics tracking layer, ensuring that user tokens and personal identifiers are never attached to event parameters.

## Interview answer — deep senior

In high-assurance mobile engineering, side-channel data leakage often exposes sensitive credentials long before an attacker attempts to break cryptographic storage.
Developers diligently encrypt local databases while inadvertently uploading plaintext bearer tokens to third-party analytics dashboards.
To establish robust defense-in-depth, we systematically seal each exfiltration vector at the architectural layer.
For application logging, relying on developer discipline to omit Log.d statements is an antipattern.
We enforce automated removal by instructing R8 with -assumenosideeffects to strip all android.util.Log calls from the release bytecode during compilation.
For the user interface layer, the operating system routinely captures screen snapshots when users navigate home, storing unencrypted bitmap images of the application state in system caches.
Applying WindowManager.LayoutParams.FLAG_SECURE prevents these snapshots from being written to disk and renders the window black in the recent apps overview.
For observability channels like Crashlytics and network monitoring, we treat third-party servers as untrusted sinks.
In OkHttp, we configure HttpLoggingInterceptor with explicit redactHeader rules for Authorization and Cookie headers, and disable body logging entirely in release builds.
In our crash reporting and analytics abstraction layers, we run all breadcrumb metadata and event bundles through a regex-based sanitization pipeline that detects and masks JWT patterns, credit card PAN numbers, and email addresses prior to SDK ingestion.
This guarantees that an infrastructure compromise at a third-party analytics vendor does not result in a catastrophic credential breach for our customers.

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
