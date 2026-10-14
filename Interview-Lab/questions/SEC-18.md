---
id: "SEC-18"
question: "How do you validate exported components, deep links, and PendingIntents?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 315
editorial_status: "reviewed"
---

# SEC-18

## Original interview question

How do you validate exported components, deep links, and PendingIntents?

## What the interviewer evaluates

- Exported component identity, URI/deep-link validation and PendingIntent mutability.
- Distinguishing input parsing from business authorization.

## Explanation in Arabic

كيف تتحقق من أمان المكونات المصدرة (Exported Components)، الروابط العميقة (Deep Links)، والـ PendingIntents؟

1. تأمين المكونات المصدرة (Exported Components):
   - بدءاً من Android 12 (API 31)، أصبح تحديد `android:exported="true|false"` إلزامياً لكل Activity و Service و Receiver يحتوي على Intent Filter.
   - **القاعدة الأساسية**: اجعل كل المكونات `exported="false"` ما لم تكن مخصصة صراحة للاستدعاء من تطبيقات خارجية أو النظام.
   - إذا كان المكون مصدراً لتبادل البيانات مع تطبيقاتك الأخرى التابعة لنفس الشركة، احمه بـ **Signature Permission** (`android:protectionLevel="signature"`)، بحيث يرفض النظام استدعاء المكون إلا إذا كان التطبيق المتصل موقعاً بنفس مفتاح الشهادة الخاص بك.

2. حماية الـ Deep Links ومنع الـ Intent Redirection:
   - الروابط العميقة التقليدية (`scheme://host/path`) يمكن لأي تطبيق خبيث على الهاتف تسجيل نفس الـ Scheme واعتراضها.
   - **الحل**: استخدام **Android App Links** المدعومة بنظام Digital Asset Links (`.well-known/assetlinks.json`) للتحقق المشفر من ملكية الدومين.
   - فحص وتطهير (Sanitize) جميع المعاملات (Query Parameters) بدقة، وتجنب استخدامها مباشرة في فتح شاشات داخلية أو WebViews لمنع ثغرات Open Redirect.

3. تأمين الـ PendingIntents (Mutability Risks):
   - الـ PendingIntent يمنح التطبيق المستلم صلاحية تنفيذ الـ Intent المرفق بصلاحيات وهوية تطبيقك الأصلي!
   - إذا تم إنشاء PendingIntent كـ `FLAG_MUTABLE`، يمكن لتطبيق وسيط تعديل الـ Action أو الـ Extras واستغلاله في اختراق التطبيق أو تسريب بيانات.
   - **الحل الإلزامي**: استخدام `PendingIntent.FLAG_IMMUTABLE` دائماً، ولا تستخدم `FLAG_MUTABLE` إلا إذا كان الـ Intent يتطلب ملء بيانات من النظام (مثل أزرار الرد السريع في الإشعارات Direct Reply).

## Practical walkthrough

تأمين المكونات، الروابط العميقة، والـ PendingIntents ضد هجمات الـ Hijacking والـ Intent Injection:
```kotlin
// 1. إنشاء PendingIntent غير قابل للتعديل (Immutable) لتأمين الإشعارات:
fun createSecureNotificationPendingIntent(context: Context, orderId: String): PendingIntent {
    val intent = Intent(context, OrderDetailsActivity::class.java).apply {
        // تحديد المكون الصريح لمنع اعتراض الـ Intent
        putExtra("extra_order_id", orderId)
    }
    
    // استخدام FLAG_IMMUTABLE يمنع أي تطبيق خارجي من التلاعب بالـ Extras أو الـ Action
    return PendingIntent.getActivity(
        context,
        orderId.hashCode(),
        intent,
        PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
    )
}

// 2. التحقق الصارم من مدخلات الـ Deep Link ومنع الـ Open Redirect:
class DeepLinkHandlerActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val uri = intent.data ?: run { finish(); return }
        
        // التحقق من الدومين والمسار لمنع الـ Path Traversal أو الـ Injections
        if (uri.scheme == "https" && uri.host == "pay.example.com") {
            val safeTarget = when (uri.path) {
                "/checkout" -> {
                    val rawToken = uri.getQueryParameter("token")
                    if (isValidTokenFormat(rawToken)) Screen.Checkout(rawToken) else Screen.Error
                }
                else -> Screen.Home
            }
            navigateTo(safeTarget)
        } else {
            finish() // رفض أي روابط غير معروفة فوراً
        }
    }
    private fun isValidTokenFormat(token: String?): Boolean = token?.matches(Regex("^[a-zA-Z0-9_-]{16,64}$")) == true
}
```

## Why it matters and how it works

Android resolves intents to exported activities/services/receivers/providers according to manifest filters. Deep links can carry attacker-controlled inputs. A PendingIntent delegates the creating app’s identity to another holder, so explicit targets and `FLAG_IMMUTABLE` are preferred unless mutation is required. Validate URI scheme/host/path and business state separately.

## Worked example

Android example: a notification opens an explicit app activity with an opaque operation ID. `PaymentReturnActivity` is the application's component; it re-fetches the authenticated user's status from the backend and never trusts an `approved` extra or deep-link amount.

```kotlin
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.net.Uri

fun paymentReturnIntent(context: Context, operationId: String): PendingIntent {
    val intent = Intent(context, PaymentReturnActivity::class.java)
        .putExtra("operationId", operationId)
        .setData(Uri.Builder().scheme("app").authority("payment-return")
            .appendPath(operationId).build()) // distinct PendingIntent identity
    return PendingIntent.getActivity(
        context,
        0,
        intent,
        PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_ONE_SHOT,
    )
}
// PaymentReturnActivity is an application type; it must validate and fetch status.
```

## Trade-offs and decision criteria

Exporting is necessary for legitimate entry points, but each adds an external surface. App Links can improve domain association but do not eliminate malicious parameter values or backend authorization. Mutable PendingIntents are justified only for specific fill-in flows.

## Failure modes

An exported receiver accepts an intent extra `admin=true` and invokes a privileged action. Another app can send that intent. Require a protected entry point and server permission check; fuzz malformed URIs and unexpected extras.

## Production perspective

CI inspects merged manifests for unintended exports, tests hostile intents and deep links, and reviews PendingIntent flags across supported Android versions. Financial state is fetched from the backend using session identity and operation ID.

## Interview answer — short

Set android:exported="false" unless public access is required, and protect inter-app components with signature permissions. For PendingIntents, strictly use FLAG_IMMUTABLE to prevent malicious payload mutation. For deep links, enforce verified Android App Links and strictly validate query parameters to prevent intent redirection and path traversal.

## Interview answer — structured

Securing IPC boundaries requires rigorous controls across components, deep links, and intents.

First, unintentionally exported components create unauthorized entry points into private business logic. Mark all Activities, Services, and Receivers `android:exported="false"` unless explicitly required. For multi-app suites sharing components, enforce custom permissions with `android:protectionLevel="signature"`. Next, a PendingIntent Immutability is a `PendingIntent` executes with the permissions and identity of the creating application. If flagged `FLAG_MUTABLE`, receiving applications can mutate the wrapped intent's action, data, or flags—enabling Intent Redirection attacks. Always apply `PendingIntent.FLAG_IMMUTABLE` unless interaction requires runtime system completion (such as Inline Reply in notifications).
Finally, with Deep Link Validation & App Links, custom URI schemes (`scheme://`) lack ownership verification and can be claimed by malicious apps. Use **Android App Links** with SHA-256 assetlinks verification on the server. Never pass deep link URLs directly to internal WebViews or invoke component launch intents dynamically based on untrusted intent extras.


## Interview answer — deep senior

From a threat modeling perspective, Intent-based attacks represent a significant vulnerability surface in Android applications.

First, an Intent Redirection / Proxying Vulnerability is a common flaw occurs when an exported Activity extracts an untrusted `Intent` from its extras (e.g., `intent.getParcelableExtra("target_intent")`) and invokes `startActivity(targetIntent)`. An attacker can construct an intent pointing to an unexported internal activity, effectively bypassing `exported="false"` using the victim app as an unintentional proxy. Next, with PendingIntent Hijacking in Foreground Services, when creating `PendingIntent` instances for notifications or alarms, ensure the wrapped Intent explicitly targets a concrete component class name (`setClass()` or `setComponent()`). Implicit intents wrapped in PendingIntents can be intercepted by rival apps registered for the matching intent filter.
Finally, with Automated Manifest Auditing, run automated CI static analysis (e.g., Android Lint `ExportedService`, `UnspecifiedImmutableFlag`) to block builds containing unreviewed exported declarations or mutable pending intents.


## How to answer in the interview

- **Why:** exported entry points accept attacker-controlled data.
- **How:** parse links defensively, validate server state, and constrain PendingIntent mutability and targets.
- **Trade-off:** stricter exports can limit intended integrations.
- **Failure case:** deep link amount becomes authorization.
- **Production solution:** malicious-intent tests and manifest/URI grant audit.

## Deep-dive talking points

Prompt for manifest export audit, caller identity, URI parsing, explicit immutable PendingIntents, and server-side payment verification.

## Follow-up questions

- **Interviewer:** "When is PendingIntent.FLAG_MUTABLE legitimately required?"
  **Answer:** "When the receiving process must fill in intent extras, such as Android Notification Inline Reply actions or Geofence transition data."

- **Interviewer:** "What is the difference between Android Deep Links and Android App Links?"
  **Answer:** "Deep Links use custom schemes without verification and trigger an app picker disambiguation dialog; App Links use HTTPS and verify domain ownership via Digital Asset Links to open directly without prompts."

## Self-check rubric

Can I test a hostile intent, explain PendingIntent delegation, and reject deep-link parameters as authorization?

## References and reviewed-on date

- [Android exported component guidance](https://developer.android.com/privacy-and-security/risks/android-exported) — component exposure.
- [PendingIntent security](https://developer.android.com/privacy-and-security/risks/pending-intent) — mutability risk.

Technically reviewed against primary documentation on 2026-10-13.
