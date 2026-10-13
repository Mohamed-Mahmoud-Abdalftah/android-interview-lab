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

An Intent is an asynchronous messaging object requesting an action: Explicit specifies the exact target component, while Implicit declares an action for the OS to resolve. A PendingIntent is a security wrapper granting another application or the OS system server permission to execute your Intent with your app's identity and privileges in the future.

## Interview answer — structured

An **`Intent`** is an operational message that requests an action from an Android component:

- **Explicit Intent**: Explicitly names the target component class (`Intent(context, TargetActivity::class.java)`). Used almost exclusively for internal application navigation.
- **Implicit Intent**: Declares a general action to perform (e.g., `Intent.ACTION_DIAL` with `tel:123`, or `ACTION_SEND` for sharing). The Android OS queries all package manifests for matching `<intent-filter>` declarations and displays the system app chooser.

A **`PendingIntent`** is a security token wrapping an Intent. It delegates execution permission to a foreign application or system process—most commonly `NotificationManager`, `AlarmManager`, or App Widgets. When triggered, the system executes the pre-configured Intent with the permissions and identity of *your application*, even if your app's process is currently dead.

## Interview answer — deep senior

At the systems and security architecture level, a `PendingIntent` is essentially an IPC handle referencing a token maintained by the system's `ActivityManagerService` (AMS). Because foreign apps execute it using your app's Linux UID, security vulnerabilities historically arose if malicious apps mutated the underlying intent parameters.

Starting in Android 12 (API 31), the platform mandates declaring mutability flags on every `PendingIntent`:

- **`FLAG_IMMUTABLE`**: The default standard. Freezes the Intent parameters completely; the receiving app or system cannot modify its extras or URI.
- **`FLAG_MUTABLE`**: Allows callers to inject extra parameters via `fillIn()`. Only used in specialized features like notification inline replies or bubbles.

Attempting to create a `PendingIntent` without declaring one of these flags on Android 12+ crashes immediately with an `IllegalArgumentException`.

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
