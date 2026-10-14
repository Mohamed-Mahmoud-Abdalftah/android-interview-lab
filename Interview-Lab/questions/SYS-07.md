---
id: "SYS-07"
question: "Design a notification system with deep links."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "A"
phase: 4
priority: "P1"
order: 336
editorial_status: "reviewed"
---

# SYS-07

## Original interview question

Design a notification system with deep links.

## What the interviewer evaluates

Design notification delivery with server authority, deep links and security validation.

## Explanation in Arabic

كيف تصمم نظام إشعارات (Push Notifications) مع روابط عميقة (Deep Links) يتعامل مع كل حالات فتح التطبيق (Cold, Warm, Background)؟

1. معمارية تدفق الإشعارات في أندرويد:
   - **Data Messages vs. Notification Messages في FCM**:
     * **Notification Messages**: إذا كان التطبيق في الخلفية، يعرض النظام الإشعار في الـ System Tray تلقائياً دون استدعاء كودك، ويمرر الـ Intent عند نقر المستخدم فقط.
     * **Data Messages (المفضلة هندسياً)**: يُستدعى `FirebaseMessagingService.onMessageReceived()` دائماً في كود تطبيقك سواء كان التطبيق مفتوحاً أو في الخلفية، مما يسمح لك ببناء إشعار مخصص، تشفير البيانات، والتحكم التام بالـ PendingIntent.

2. تصميم الـ Deep Link Router الموحد:
   - **تجنب الفخ الشائع**: فتح الشاشة المستهدفة مباشرة (مثل شاشة تفاصيل الطلب `OrderDetailsActivity`) بشكل منعزل! إذا ضغط المستخدم على زر الرجوع (Back Button)، يُغلق التطبيق فوراً ويخرج للشاشة الرئيسية للهاتف بدلاً من الرجوع للـ Home Screen!
   - **الحل عبر TaskStackBuilder**: بناء الـ Back Stack برمجياً بحيث يضمن أن الرجوع من شاشة الطلب يعود إلى شاشة قائمة الطلبات ثم الـ Home Screen.

3. التعامل مع حالات الـ Cold Start والمصادقة (Auth State Guard):
   - إذا نقر المستخدم على إشعار بتفاصيل معاملة بنكية ولكن جلسته منتهية (Unauthenticated):
   - يجب أن يوجهه الـ Router لشاشة تسجيل الدخول أولاً، مع حفظ الـ Deep Link كـ Pending Navigation Destination، وبعد نجاح الدخول يتم توجيهه تلقائياً للهدف الأصلي.

## Practical walkthrough

تنفيذ معمارية توجيه الإشعارات وبناء الـ Back Stack وحماية مسارات المصادقة:
```kotlin
class PushNotificationHandler(private val context: Context) {
    fun showOrderNotification(orderId: String, title: String, message: String) {
        // 1. إنشاء Intent الشاشة المستهدفة مع معرّف الطلب:
        val targetIntent = Intent(context, OrderDetailsActivity::class.java).apply {
            putExtra("extra_order_id", orderId)
        }

        // 2. استخدام TaskStackBuilder لبناء الـ Back Stack الطبيعي (Home -> Orders -> OrderDetails):
        val pendingIntent = TaskStackBuilder.create(context).run {
            // إضافة الكلاس الأم تلقائياً كما هو معرف في AndroidManifest أو يدوياً:
            addNextIntentWithParentStack(targetIntent)
            getPendingIntent(
                orderId.hashCode(),
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
        }

        // 3. بناء الإشعار وعرضه عبر NotificationManager
        val notification = NotificationCompat.Builder(context, "orders_channel")
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(message)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .build()

        NotificationManagerCompat.from(context).notify(orderId.hashCode(), notification)
    }
}
```

## Why it matters and how it works

Use notification payload as a hint/identifier, not trusted authorization or secret data. Persist user-visible inbox/history server-side if delivery matters. Android 13+ notification runtime permission affects display; channel configuration affects user control. Deep links must validate URI/arguments and avoid open redirects.

## Worked example

Conceptual deep-link contract; actual NavHost and PendingIntent flags must be configured per target SDK.

```kotlin
data class NotificationTarget(val eventId: String, val resourceId: String)
interface NotificationRouter {
    suspend fun resolve(target: NotificationTarget, session: Session): Route
}
// Resolve by authenticated server lookup; never trust a push payload
// as proof that the resource belongs to the current account.
```

## Trade-offs and decision criteria

Push is low latency and battery-efficient, but can be delayed, dropped or disabled; server inbox plus sync gives recoverability. Deep links improve UX but broaden attack surface. Notification content should minimize sensitive data on lock screen.

## Failure modes

Trusting a resource ID from a forged link can expose another user’s item. A notification tapped after logout can navigate to stale private content. Duplicate push can display twice without event IDs. Permission denial means no visible notification even though server event exists.

## Production perspective

A messaging app stores messages on backend, sends push with opaque event ID, deduplicates local display and on tap fetches authorized conversation state. After login it resumes destination; tests cover cold start, old app version, disabled notifications and malicious URI.

## Interview answer — short

Design notifications using FCM data-payload messages for deterministic client processing. Construct synthetic back stacks using TaskStackBuilder so pressing Back navigates to parent screens rather than exiting the app. Intercept routing through an AuthGuard to handle expired sessions before resuming deep link navigation.

## Interview answer — structured

Designing a reliable push notification and deep linking system requires coordinating across background delivery, synthetic navigation hierarchies, and session states.

First, **FCM Payload Strategy**. Next, prefer FCM **Data Messages** over standard Notification messages. Data messages invoke `onMessageReceived()` deterministically regardless of whether the app is in foreground, background, or killed, allowing client decryption, local database caching, and custom notification rendering.
**Synthetic Back Stack (TaskStackBuilder)**. Direct navigation to a deep link destination creates a broken back stack where pressing the system Back button terminates the application. Use `TaskStackBuilder.create(context).addNextIntentWithParentStack(targetIntent)` to synthesize a natural navigation path (e.g., Home -> Orders -> OrderDetail).
**Authentication & Session Interception (AuthGuard)**. Finally, when an unauthenticated or logged-out user clicks a sensitive push notification, the deep link router must store the pending destination in memory/DataStore, redirect the user through the Login/MFA flow, and resume navigation to the original deep link target upon successful authentication.


## Interview answer — deep senior

From a staff-level systems perspective, deep link architectures must support single-activity Compose routing and cold-boot resilience.

First, with Single-Activity Jetpack Compose Routing, in modern Single-Activity apps, route deep links to a single `MainActivity` with `launchMode="singleTask"`. Override `onNewIntent(intent: Intent?)` to capture incoming notifications when the app is already running, updating a reactive `NavigationEvents` channel consumed by the top-level Compose `NavHost`. Next, with Cold Start Race Conditions, during a cold launch triggered by a notification tap, the app must initialize dependency graphs, load remote feature flags, and restore session credentials before executing the navigation transition. Queue the pending deep link event in an application-scoped state machine until baseline startup initialization signals readiness.
Finally, with Deep Link Security & Parameter Sanitization, treat all intent parameters as untrusted external input. Validate UUID formats, sanitize URIs, and prevent open redirects where malicious URLs could instruct the app to launch arbitrary internal activities or WebViews.


## How to answer in the interview

- **Why:** push delivery and user context are not guaranteed.
- **How:** store server event identity, route taps through authenticated resource lookup.
- **Trade-off:** re-fetch adds latency but prevents stale or cross-account display.
- **Failure case:** duplicate push or tap after account switch.
- **Production solution:** idempotent inbox state, immutable intent, and cold-start tests.

## Deep-dive talking points

Trace event creation to authorized destination and list delivery/visibility limits.

## Follow-up questions

- **Interviewer:** "What happens if a notification uses FLAG_ACTIVITY_NEW_TASK without TaskStackBuilder?"
  **Answer:** "The target Activity opens as a standalone task root; pressing Back exits to the Android home launcher rather than parent screens."

- **Interviewer:** "How do you handle push notifications when the user is actively viewing the screen that the notification refers to?"
  **Answer:** "Detect the active foreground screen; suppress the system tray notification, update the live UI data directly via StateFlow, and optionally show a subtle in-app snackbar."

## Self-check rubric

Can I distinguish push from durable truth, validate deep links and handle duplicate/cold-start paths?

## References and reviewed-on date

- [Android notifications](https://developer.android.com/develop/ui/views/notifications) — channels and permission.
- [Android deep links](https://developer.android.com/training/app-links/deep-linking) — routing/security.

Technically reviewed against primary documentation on 2026-10-13.
