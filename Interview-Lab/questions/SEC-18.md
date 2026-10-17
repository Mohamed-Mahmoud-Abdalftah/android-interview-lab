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

## Concept and technical explanation

Validating Android component boundaries, deep links, and PendingIntents protects an application against unauthorized inter-process invocation, privilege escalation, and intent redirection attacks. Components (Activities, Services, BroadcastReceivers, ContentProviders) must declare android:exported="false" by default unless intended for external cross-app communication. When components must be exported, access should be constrained using signature-level custom permissions (android:protectionLevel="signature") or caller validation (checking Binder.getCallingUid() and PackageManager.hasSigningCertificate()). For deep links, custom URL schemes (like myapp://) provide zero cryptographic verification and are vulnerable to scheme hijacking by malicious third-party apps; enterprise applications mandate Android App Links, which cryptographically bind web domains to the app binary using Digital Asset Links (assetlinks.json). When constructing PendingIntents, developers must enforce FLAG_IMMUTABLE (mandated in Android 12+) to prevent malicious receiving applications from mutating the underlying Intent's action, data URI, or extras via fillIn() to hijack internal privileged workflows.

## Practical walkthrough (English)

Securing PendingIntents, component boundaries, and deep link URI validation:
```kotlin
// 1. Mandatory FLAG_IMMUTABLE for secure PendingIntent instantiation
fun createSecureNotificationPendingIntent(context: Context, orderId: String): PendingIntent {
    val explicitIntent = Intent(context, OrderDetailsActivity::class.java).apply {
        putExtra("ORDER_ID", orderId)
        // Explicit component prevents intent redirection
    }
    
    // FLAG_IMMUTABLE stops third parties from mutating extras via fillIn()
    return PendingIntent.getActivity(
        context,
        REQUEST_CODE_ORDER,
        explicitIntent,
        PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
    )
}

// 2. Strict deep link URI validation and parameter sanitization
fun sanitizeDeepLinkUri(incomingUri: Uri): String? {
    // Enforce trusted HTTPS authority rather than custom schemes
    if (incomingUri.scheme != "https" || incomingUri.host != "bank.example.com") {
        return null // Reject untrusted schemes or rogue hosts
    }
    val path = incomingUri.path ?: return null
    if (!path.startsWith("/transfer/verify")) return null

    // Sanitize query parameter to prevent path traversal or injection
    val transactionToken = incomingUri.getQueryParameter("token")
    return if (transactionToken?.matches(Regex("^[a-zA-Z0-9_-]{32,64}$")) == true) {
        transactionToken
    } else {
        null
    }
}
```

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

We secure component boundaries by setting exported to false by default or gating public endpoints with signature permissions. For deep links, we mandate Android App Links with Digital Asset Links and strictly sanitize parameters. For PendingIntents, we enforce FLAG_IMMUTABLE with explicit component intents, preventing malicious apps from hijacking internal actions.

## Interview answer — structured

Securing Android component boundaries requires strict validation of input vectors to prevent privilege escalation and unauthorized access.
All components must declare android:exported=false by default in AndroidManifest.xml.
If a component must be exported to receive external events, we protect it with custom signature permissions or verify the calling package's signing certificate using PackageManager before executing privileged actions.
For deep links, relying on custom URI schemes exposes users to link hijacking because any app can register the same scheme.
Instead, we implement Android App Links, which require hosting a digital asset links JSON file on our HTTPS domain to cryptographically verify domain ownership at install time.
When handling incoming deep links, we strictly validate URIs against an allowlist and sanitize all parameters against injection attacks.
On the Intent front, PendingIntents must always specify an explicit component and include FLAG_IMMUTABLE.
Omitting immutability allows an untrusted receiving application to modify the intent's payload using the fillIn method, redirecting execution to private application components.

## Interview answer — deep senior

Component vulnerability analysis represents one of the most prevalent attack surfaces in modern mobile development, often leading to full account takeover or local privilege escalation.
When an activity or service is marked as exported without strict permission gates, any malicious application on the device can launch it directly with forged Intent extras, bypassing login screens and business validations.
In multi-app enterprise suites, we secure exported components using signature permissions; Android enforces at the kernel and framework level that only apps signed with the identical developer certificate can invoke the component.
When deep links are introduced, standard custom URL schemes are inherently insecure because Android does not enforce unique scheme registration; two apps can register the same custom scheme, resulting in disambiguation dialogs or silent traffic interception.
Android App Links solve this through Digital Asset Links verification, ensuring our app exclusively handles the domain.
Once inside the activity, we treat the incoming Intent data URI as untrusted user input: we reject path traversal characters (such as ../), validate expected paths, and sanitize query parameters against strict regex patterns.
Regarding PendingIntents, Android 12 made explicit mutability flags mandatory for a reason.
A mutable PendingIntent granted to a third party or system notification allows a rogue application to invoke fillIn() and overwrite the intent's action, data URI, or flags.
Attackers exploit this via Intent Redirection, forcing our application to launch unexported internal components with our own elevated permissions.
Enforcing FLAG_IMMUTABLE and explicit component targeting permanently closes this vulnerability.

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
