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

## Concept and technical explanation

Designing a mobile push notification and deep-link routing system requires orchestrating multiple ingress pathways: Firebase Cloud Messaging (FCM) data/notification payloads, verified Android App Links (HTTPS), custom URI schemes, and local alarms. The architecture must accommodate all application lifecycle phases: cold start from process death, warm start from background state, and active foreground execution. Core technical requirements include: decoupling sensitive data from push payloads (passing lightweight IDs and fetching details from authenticated APIs), centralizing URI parsing and permission validation within a dedicated DeepLinkRouter, constructing logical synthetic back-stacks via TaskStackBuilder so pressing the back button navigates up to parent screens rather than exiting the application, and ensuring full compliance with Android 12+ trampoline restrictions and Android 13+ POST_NOTIFICATIONS runtime permissions.

## Practical walkthrough (English)

Implementing a secure notification dispatcher and synthetic back-stack routing:
```kotlin
// 1. Firebase Messaging Service receiving payloads and dispatching notifications
class AppFirebaseMessagingService : FirebaseMessagingService() {

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        val data = remoteMessage.data
        val targetUri = data["deep_link_uri"] ?: return
        val title = data["title"] ?: "New Notification"
        val message = data["message"] ?: ""

        sendNotification(title, message, Uri.parse(targetUri))
    }

    private fun sendNotification(title: String, message: String, deepLink: Uri) {
        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val channelId = "critical_updates_channel"

        // Construct synthetic back-stack targeting DeepLinkDispatchActivity
        val intent = Intent(this, MainActivity::class.java).apply {
            action = Intent.ACTION_VIEW
            this.data = deepLink
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }

        val pendingIntent = TaskStackBuilder.create(this).run {
            addNextIntentWithParentStack(intent)
            getPendingIntent(
                deepLink.hashCode(),
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
        }

        val notification = NotificationCompat.Builder(this, channelId)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(message)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .build()

        notificationManager.notify(deepLink.hashCode(), notification)
    }
}

// 2. Centralized Deep Link Router validating routes and user authorization
object DeepLinkRouter {
    fun route(context: Context, uri: Uri, isAuthenticated: Boolean): NavigationCommand {
        val path = uri.path ?: return NavigationCommand.ToHome

        // Route validation and auth gatekeeper
        return when {
            path.startsWith("/orders/") -> {
                val orderId = uri.lastPathSegment ?: ""
                if (isAuthenticated) {
                    NavigationCommand.ToOrderDetail(orderId)
                } else {
                    NavigationCommand.ToLogin(redirectUri = uri)
                }
            }
            path.startsWith("/promo/") -> NavigationCommand.ToPromo(uri.getQueryParameter("code") ?: "")
            else -> NavigationCommand.ToHome
        }
    }
}

sealed interface NavigationCommand {
    data object ToHome : NavigationCommand
    data class ToOrderDetail(val orderId: String) : NavigationCommand
    data class ToLogin(val redirectUri: Uri) : NavigationCommand
    data class ToPromo(val code: String) : NavigationCommand
}
```

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

We design notification and deep-link systems using Firebase Cloud Messaging, a centralized DeepLinkRouter, and TaskStackBuilder. Push payloads contain only metadata and target URIs rather than raw sensitive data. When tapped, the router parses and validates the deep link, constructs a proper synthetic back-stack so pressing back returns to the parent screen, and handles user authentication status before routing to the destination.

## Interview answer — structured

A robust push notification and deep linking architecture guarantees secure delivery, seamless routing, and proper back-stack reconstruction across all application lifecycle states.
In the data layer, our FirebaseMessagingService receives push payloads containing lightweight metadata and action URIs, never sensitive personal data.
If the app is in the background or killed, the system tray notification carries a PendingIntent targeting our centralized DeepLinkRouter.
When the user taps the notification, the router intercepts the URI, verifies user authentication state, and validates target parameters against an authorized routing registry to prevent malicious link injection.
To maintain an intuitive user experience, we use Android's TaskStackBuilder to construct a synthetic back-stack.
For example, deep linking directly into an order details screen synthesizes the order history and home screens beneath it, ensuring that pressing the back button navigates logically upward instead of abruptly exiting to the Android home screen.
If the destination requires authentication and the user is logged out, the router caches the pending deep link and resumes navigation after successful login.

## Interview answer — deep senior

From a systems architecture standpoint, handling deep links reliably requires accommodating cold starts, process death, and platform version discrepancies.
On Android 12 and above, the operating system enforces strict trampoline restrictions, blocking broadcast receivers and background services from starting activities directly.
Consequently, all notification PendingIntents must launch an Activity directly or dispatch through an immutable PendingIntent with the FLAG_IMMUTABLE flag.
In cold-start scenarios, the target screen often depends on essential asynchronous initialization, such as session validation, remote config fetching, or database decryption.
If the deep link routes immediately before these dependencies are ready, the app risks crashing or leaking unauthenticated screens.
Our architecture uses an application-level NavigationCoordinator that checks the startup readiness state.
If initialization is pending, the coordinator enqueues the deep-link command until authentication and configuration resolve.
Furthermore, we implement Android App Links with verified digital asset links on the web server, ensuring that verified HTTPS URLs open our app directly without displaying the ambiguous Android disambiguation dialog.
Finally, we sanitize all incoming URI query parameters against path traversal and SQL injection vectors before passing arguments to ViewModels, safeguarding internal application boundaries.
We also configure notification channels with clear user-facing importance levels and manage dynamic badge counts through OEM-compatible badge APIs, ensuring consistent visual affordance across varied device manufacturers.

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
