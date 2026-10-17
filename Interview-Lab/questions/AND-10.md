---
id: "AND-10"
question: "What are Intent and PendingIntent? Explain explicit versus implicit intents."
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "A"
phase: 1
priority: "P1"
order: 40
editorial_status: "reviewed"
---

# AND-10

## Original interview question

What are Intent and PendingIntent? Explain explicit versus implicit intents.

## What the interviewer evaluates

- Distinguish a message used now from a token another actor can invoke later.
- Explain component-targeted explicit versus action/data-based implicit resolution.
- Choose safe `PendingIntent` target, mutability, identity, and validation for notifications.

## Concept and technical explanation

In the Android operating system, an Intent is an asynchronous messaging object used to request an action from another app component or to broadcast system-wide events. Intents serve as the fundamental inter-process communication (IPC) abstraction binding Activities, Services, and BroadcastReceivers.

Intents are categorized into two core types:
1. Explicit Intent:
Designates the target component explicitly by specifying either its fully qualified Java or Kotlin class name (such as Intent(context, OrderDetailsActivity::class.java)) or an explicit component identifier. Because the target is predetermined, the runtime routes the message directly to that component within the application or a known target package. Explicit intents are type-safe, fast, and secure.

2. Implicit Intent:
Specifies an abstract general action to be performed (such as ACTION_VIEW, ACTION_SEND, or ACTION_DIAL) alongside data URIs, MIME types, and categories, without declaring the destination class. When launched, the Android PackageManagerService queries all installed applications on the device, matching the intent against registered intent-filters declared in their manifests. If multiple applications match, the system displays an app chooser dialog.

In contrast, a PendingIntent is a token of authorization granted to an external system service or foreign application (such as NotificationManager, AlarmManager, or AppWidgetHost). It encapsulates an underlying Intent along with a delegate permission grant: it authorizes the external process to fire the encapsulated Intent at a future timestamp with the exact identity, Linux User ID (UID), and permissions of the originating application, even if the originating application process is terminated. Modern Android (API 31+) mandates declaring explicit mutability flags (FLAG_IMMUTABLE or FLAG_MUTABLE) to prevent malicious intent modification and hijacking.

## Practical walkthrough (English)

Constructing and dispatching a secure PendingIntent for a system notification:
```kotlin
// 1. Construct the explicit internal intent with payload
val intent = Intent(context, OrderDetailsActivity::class.java).apply {
    putExtra("order_id", "ORD-12345")
    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
}

// 2. Wrap in PendingIntent with mandatory security flags
val pendingIntent = PendingIntent.getActivity(
    context,
    ORDER_REQUEST_CODE,
    intent,
    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE // Mandatory on Android 12+
)

// 3. Attach to NotificationCompat.Builder
val notification = NotificationCompat.Builder(context, CHANNEL_ID)
    .setContentTitle("Order Shipped")
    .setContentText("Tap to view your tracking details")
    .setSmallIcon(R.drawable.ic_shipping)
    .setContentIntent(pendingIntent)
    .setAutoCancel(true)
    .build()
```
Failure scenario:
If an engineer declares an implicit Intent inside a PendingIntent or omits FLAG_IMMUTABLE, a malicious third-party application on the device can intercept the pending token, alter the embedded Intent's extras or target component (Intent Hijacking), and execute privileged code with the victim application's permissions.

## Explanation in Arabic

الـ `Intent` والـ `PendingIntent` هما رسائل التواصل بين المكونات في نظام Android:

1. ما هو الـ `Intent`؟
   - هو **كائن رسالة يصف نية لتنفيذ عملية (Messaging Object)**.
   - **نوعان رئيسيان:**
     * **Explicit Intent (صريح):** يحدد اسم الكلاس المستهدف بدقة داخل تطبيقك (`Intent(context, ProfileActivity::class.java)`). آمن وسريع.
     * **Implicit Intent (ضمني):** يحدد **الأكشن المطلوب** بدون تحديد الكلاس (مثل: `ACTION_VIEW` لفتح رابط موقع، أو `ACTION_SEND` لمشاركة نص). نظام أندرويد يفحص التطبيقات المثبتة التي تدعم هذا الأكشن في الـ Intent Filter ويعرض للمستخدم قائمة للاختيار منها.

2. ما هو الـ `PendingIntent`؟
   - هو **رمز تفويض وتوكيل رسمي (Token of Authorization)** تمنحه لتطبيق خارجي أو لنظام التشغيل (مثل نظام الإشعارات أو Widget).
   - يسمح للنظام أو التطبيق الخارجي بتنفيذ الـ Intent المحفوظ بداخله **باسم تطبيقك وبصلاحيات تطبيقك أنت (With your app's permissions and identity)** في وقت لاحق، حتى لو كان تطبيقك مغلقاً تماماً!

3. الأمان الإلزامي في أندرويد الحديث (Android 12+):
   - فرض تحديد `FLAG_IMMUTABLE` أو `FLAG_MUTABLE` عند إنشاء أي PendingIntent لمنع ثغرات التلاعب بالـ Intent.

## Practical walkthrough

تطبيق عملي: فتح تفاصيل الطلب عند الضغط على Notification:
```kotlin
// 1. إنشاء Explicit Intent صريح للشاشة المستهدفة:
val intent = Intent(context, OrderDetailsActivity::class.java).apply {
    putExtra("order_id", "ORD-12345")
}

// 2. تغليفه في PendingIntent وتفويض نظام الإشعارات لتشغيله:
val pendingIntent = PendingIntent.getActivity(
    context,
    REQUEST_CODE,
    intent,
    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE // إلزامي في أندرويد 12+
)

// 3. إرفاقه بالإشعار:
NotificationCompat.Builder(context, CHANNEL_ID)
    .setContentIntent(pendingIntent) // عند ضغط المستخدم يفتح الشاشة بتصريح تطبيقك
    .build()
```

## Why it matters and how it works

Android resolves an explicit Intent to its named component. An implicit Intent describes an action/data type and is matched against exported filters, potentially showing a chooser. A PendingIntent is a system-managed capability that wraps an Intent for later invocation by a holder such as the notification manager. Its identity and update flags affect whether old extras are reused or replaced. Mutability must be explicit for apps targeting Android 12+, and modern target-SDK restrictions make mutable implicit PendingIntents especially unsafe. The receiver still validates every input and current account state.

## Worked example

For a receipt notification, make the target explicit and give each receipt a distinct Intent identity. This Android snippet assumes a `ReceiptActivity`, a validated opaque `receiptId`, and a Context from the notification builder's owner.
```kotlin
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.net.Uri

fun receiptTap(context: Context, receiptId: String): PendingIntent {
    val route = Uri.Builder().scheme("app").authority("receipt")
        .appendPath(receiptId).build()
    val intent = Intent(context, ReceiptActivity::class.java).apply {
        data = route // Intent identity includes data; extras alone do not distinguish taps.
        putExtra("receipt_id", receiptId)
    }
    return PendingIntent.getActivity(
        context, 0, intent,
        PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
    )
}
```
`ReceiptActivity` must authenticate and fetch the receipt from a backend that checks ownership; the extra is never proof of authorization. For sharing text externally, use an implicit `ACTION_SEND` chooser. Test task-stack behavior separately.

## Trade-offs and decision criteria

Explicit Intents are predictable for internal navigation and services; implicit Intents enable user choice for external capabilities but can have no handler or resolve to an untrusted handler. Immutable PendingIntents limit what a holder can change, but a mutable one may be required for a documented inline-reply flow. `FLAG_UPDATE_CURRENT` can update creator-supplied extras even for an immutable PendingIntent, so carefully choose identity and avoid mixing users or receipt IDs in one token.

## Failure modes

An implicit Intent used for a private Service can resolve unexpectedly or be rejected. A mutable PendingIntent with broad fields can let its holder redirect an operation. Reusing the same request code for multiple notifications can show the wrong receipt if identity is not designed. A notification tap after logout can reveal stale private data if the Activity trusts extras. Test multiple simultaneous notifications, account switching, process recreation, absent handlers, and malicious extras.

## Production perspective

An order app creates a distinct explicit immutable PendingIntent per notification identity, with only an opaque order ID. The destination reconstructs navigation and checks authentication and backend ownership. Its CI inspects target-SDK behavior and tests tap flows after process death. External share flows use a chooser and temporary URI grants rather than placing private file paths in unrestricted extras.

## Interview answer — short

An Intent is a messaging object requesting an action from a component: explicit intents name the target class directly, while implicit intents declare an abstract action resolved by the OS through intent filters. A PendingIntent is a security token granting an external process permission to execute a preconfigured Intent with the originating app's identity and privileges.

## Interview answer — structured

An Intent is Android's core messaging abstraction, facilitating both intra-process and cross-process communication between Activities, Services, and BroadcastReceivers. It encapsulates the action to be performed, target data URIs, and optional bundle extras.

Intents divide into explicit and implicit variants. An explicit intent specifies the target component class directly, ensuring predictable, internal routing. In contrast, an implicit intent declares a generalized action, such as sharing content or viewing a web URL, prompting the operating system's PackageManagerService to resolve matching components across installed applications via their manifest intent filters.

A PendingIntent wraps an Intent with delegated execution rights. It passes a token to external system actors, such as NotificationManager, AlarmManager, or AppWidgetHost. When triggered, the receiving system service fires the embedded Intent with the exact Linux identity and permissions of the originating application, even if its process is currently dead.

In production, security is paramount. Starting in Android 12, developers must explicitly designate every PendingIntent as either FLAG_IMMUTABLE or FLAG_MUTABLE. Defaulting to immutable prevents malicious applications from modifying the underlying intent parameters and executing unauthorized privilege escalation.


## Interview answer — deep senior

At the operating system and Linux kernel boundary, Intents and PendingIntents leverage the Binder inter-process communication driver and the system_server's ActivityTaskManagerService. When startActivity(intent) is invoked, the call marshals the Intent structure across Binder to the system server. For explicit intents, the system server directly accesses the target package's ComponentInfo. For implicit intents, PackageManagerService executes an Intent Resolution algorithm, querying its internal IntentResolver tables against registered IntentFilters, evaluating actions, categories, data schemes, and MIME types.

The internal architecture of a PendingIntent is fundamentally different from a standard Intent. A PendingIntent does not pass an executable object; instead, it registers an IIntentSender IPC Binder interface inside the system_server process. The system server maintains an internal PendingIntentRecord that stores the calling application's Linux UID, package name, request code, target Intent, and execution flags.

Because the token is maintained by the system server, when a notification or alarm triggers the token, ActivityTaskManagerService dispatches the intent attributing all security permissions and identity to the originating UID rather than the caller's UID. Historically, this presented a critical security vulnerability known as Intent Redirection or Hijacking (CWE-927). If a PendingIntent was mutable, a malicious receiver could populate the empty Intent fields, redirecting the target component to internal, non-exported Activities containing sensitive financial or user data.

To permanently close this attack surface, Android 12 (API level 31) made declaring FLAG_IMMUTABLE or FLAG_MUTABLE mandatory. A Staff engineer enforces immutable tokens by default, reserving FLAG_MUTABLE exclusively for system integrations that require dynamic payload injection, such as inline notification replies via RemoteInput or custom camera capture URIs.

## How to answer in the interview

- **Why:** Intents route work; PendingIntents delegate future execution under the creator’s identity.
- **How:** Contrast explicit target, implicit resolution, and notification tap token.
- **Trade-offs:** Use immutable PendingIntent unless a documented interaction requires mutation.
- **Failure cases:** Mention identity collisions, untrusted extras, and wrong task stack.
- **Production solution:** Open one receipt by opaque ID and re-authorize from the backend.

## Deep-dive talking points

Explain Intent resolution, exported component boundaries, PendingIntent capability semantics, mutability rules, request-code identity, stale extras, notification back stack, and resource authorization after tap.

## Follow-up questions

- **Interviewer:** "What is `FLAG_UPDATE_CURRENT` in a PendingIntent?"
  **Answer:** "If a PendingIntent with the same RequestCode and target already exists in the system server, `FLAG_UPDATE_CURRENT` keeps the existing token but updates its extra bundle with the new Intent's extras."

- **Interviewer:** "Why must you check `resolveActivity()` before calling `startActivity(implicitIntent)`?"
  **Answer:** "If an implicit Intent has no matching apps installed on the device (e.g., calling an email app on a device without email clients), calling `startActivity()` throws an unhandled `ActivityNotFoundException` crash. You must verify resolution or wrap it in a try-catch."

- **Interviewer:** "How does `FLAG_CANCEL_CURRENT` differ from `FLAG_UPDATE_CURRENT`?"
  **Answer:** "`FLAG_CANCEL_CURRENT` cancels the existing PendingIntent token entirely before creating a new one, ensuring any previous notifications holding that token are invalidated."

## Self-check rubric

Define Intent and PendingIntent separately; contrast explicit and implicit resolution; choose mutability for a receipt tap; explain one identity collision; and place authorization after delivery.

## References and reviewed-on date

- [Intents and intent filters](https://developer.android.com/guide/components/intents-filters) — resolution and PendingIntent usage.
- [PendingIntent security](https://developer.android.com/privacy-and-security/risks/pending-intent) — mutability and capability risks.

Technically reviewed against primary documentation on 2026-10-13.
