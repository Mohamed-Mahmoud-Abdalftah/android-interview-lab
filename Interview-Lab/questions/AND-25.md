---
id: "AND-25"
question: "How would you support predictable navigation after notification taps and process recreation?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "C"
phase: 1
priority: "P1"
order: 55
editorial_status: "reviewed"
---

# AND-25

## Original interview question

How would you support predictable navigation after notification taps and process recreation?

## What the interviewer evaluates

- Build an expected back stack for a cold notification entry.
- Make pending intent identity and mutability explicit, and validate its untrusted input.
- Restore screen state from stable identifiers when the process and session have changed.

## Explanation in Arabic

الـnotification tap ممكن يفتح التطبيق وهو مقفول تمامًا، من غير أي navigation history أو ViewModel قديم. لازم تحدد المستخدم لما يضغط Back يروح فين: لو destination جزء طبيعي من التطبيق ابني parent stack مناسب بـ`TaskStackBuilder` أو جهّز graph داخل Navigation؛ لو شاشة مستقلة فعلًا قد يكون لها task مختلف. `PendingIntent` لازم تحدد mutability وupdate semantics، وتخلي request code/URI يميز الإشعارات المختلفة عشان ما يفتحش آخر order بدل المطلوب. مرّر order ID فقط، وبعد الفتح حمّل التفاصيل من repository وافحص login والauthorization؛ الـIntent ليس دليل ثقة. بعد process death نفس المسار لازم يشتغل.

## Why it matters and how it works

Notifications are external entry points. Android may start an Activity into an existing task or create a new task after the app process is gone. The content intent carries a PendingIntent that the system executes later; extras and identity need deliberate design because PendingIntent reuse can replace or retain old values. For ordinary navigation, a parent stack allows Back to step through expected hierarchy. On recreation, the Activity or NavHost rebuilds a route from a stable item ID and loads current data. The user may be logged out or the item may have been deleted since the notification was posted.

## Worked example

An order notification can build a parent stack for cold launch. This Android snippet assumes `OrderActivity` has a parent Activity declared in the manifest and that the destination safely parses an opaque order ID. The unique `data` URI distinguishes Intents even with request code `0`.
```kotlin
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.core.app.TaskStackBuilder

fun orderTap(context: Context, orderId: String): PendingIntent {
    val intent = Intent(context, OrderActivity::class.java).apply {
        data = Uri.Builder().scheme("app").authority("order")
            .appendPath(orderId).build()
        putExtra("order_id", orderId)
    }
    return requireNotNull(
        TaskStackBuilder.create(context)
            .addNextIntentWithParentStack(intent)
            .getPendingIntent(
                0, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
    )
}
```
The destination fetches the order after current-account authorization and handles missing or signed-out states. Test Back and Up for the app's actual task/Navigation setup; a different architecture may route through a single host Activity instead.

## Practical walkthrough

notification tap لازم يفتح order المقصود سواء process عايشة أو اتقتلت. استخدم explicit Activity PendingIntent بهوية مختلفة لكل order/action، و`FLAG_IMMUTABLE` لما ما تحتاجش تعديل من طرف تاني؛ راجع update flag عشان data الجديدة ما تتخلطش بnotification قديمة. Activity/NavHost تقرأ opaque order ID وتعيد بناء route/back stack منطقي، ثم repository تطلب order بعد auth/ownership check. لو order اتحذف أو account اتبدل، اعرض missing/sign-in بدل crash. اختبر نقر notification مختلفة بالتتابع، app warm/cold، Back/Up، process recreation وtask switching؛ single test من launcher مش كفاية.

## Trade-offs and decision criteria

`TaskStackBuilder` is appropriate for a normal Activity hierarchy; a special isolated destination can use a separate-task pattern, but it changes Back expectations. Navigation libraries can synthesize an in-app destination stack when the app uses one host Activity. Immutable PendingIntents reduce tampering for fixed actions; mutable ones are needed only for specific fill-in use cases and require extra care. Stable IDs are safer than bundling a stale serialized Order.

## Failure modes

Two notifications share PendingIntent identity and both open the latest order. Back exits immediately instead of revealing the expected parent. A cold Activity reads a null singleton and crashes. A deleted order renders stale data. An implicit or mutable PendingIntent exposes an unnecessary injection surface. Test multiple simultaneous notifications, existing and killed process, signed-out return, deleted item, task switch, Back and Up on supported versions.

## Production perspective

Create a notification routing contract with explicit destination type and stable entity ID. Authorization and data loading happen after launch. Preserve any pending action only if it can safely resume after sign-in; otherwise route to a safe home screen. Instrument tap-to-destination success, missing-item outcome, and crash rate without sensitive payloads. A UI test kills the process before tapping two distinct order notifications and asserts correct ID and Back behavior.

## Interview answer — short

“I design notification taps as cold external launches: supply a stable destination ID, construct the expected back stack, validate authorization, and rebuild data after process death. PendingIntent identity and mutability must be deliberate.”

## Interview answer — structured

For an ordinary destination I create a content PendingIntent and a parent stack, or configure the app's navigation graph to produce equivalent Back behavior. Each notification has a distinct identity so the system does not reuse stale extras. The launched screen accepts a stable ID and loads current data rather than depending on in-memory state. It handles signed-out and missing-item cases. I test multiple notifications, warm and cold launch, process recreation, and both Back and Up.

## Interview answer — deep senior

A notification can outlive the process, the session, and even the underlying entity. I therefore treat it as an untrusted external route, not a shortcut into an existing ViewModel. The PendingIntent is explicit, uses the least mutability required, and has identity chosen so distinct notifications do not collide. I choose a normal parent stack or a special task based on product navigation expectations, then verify Back and Up after a cold launch. The route carries a small stable ID; a repository fetches current data and checks account authorization. If the session expired, sign-in or a safe destination takes over.

For an order-delivered notification, I make each content Intent distinct using stable route data or a suitable request identity; extras alone can collide under PendingIntent matching. I normally set `FLAG_IMMUTABLE`, choose the update behavior deliberately, and construct a parent stack when this is a regular Activity destination. A single-Activity NavHost may instead route internally after launch. On cold or restored process entry, the destination reads only an opaque order ID, authenticates the current account, and fetches authorized data; missing or deleted orders get a safe state. I test two notifications in sequence, Back and Up, task switching, and process kill.

## How to answer in the interview

- **Why:** Notification entry can start a fresh process and task.
- **How:** Build a distinct explicit PendingIntent and reconstruct the destination from a stable ID.
- **Trade-offs:** Choose task-stack behavior and immutable/update flags deliberately.
- **Failure cases:** Name PendingIntent identity collisions, stale extras, and unauthorized order display.
- **Production solution:** Test multiple notifications across warm, cold, restored, Back, and Up paths.

## Deep-dive talking points

Discuss PendingIntent identity, immutable versus mutable flags, task stack, Back versus Up, stale entities, session expiry, and cold-start testing.

## Follow-up questions

- Why can two notifications open the same item? **Answer:** PendingIntents with the same identity can be reused; distinguish requests and apply intentional update semantics.
- Is the order ID inside an Intent trusted? **Answer:** no; load and authorize the entity against the current user.
- What if the app process has been killed? **Answer:** recreate navigation from the Intent and saved state, then load durable data without relying on prior in-memory objects.

## Self-check rubric

Design a cold route, a parent stack, distinct PendingIntent identities, safe data loading, and tests for expired session and process death.

## References and reviewed-on date

- [Start an Activity from a Notification](https://developer.android.com/develop/ui/views/notifications/navigation) — parent-stack and special activity patterns.
- [PendingIntent API](https://developer.android.com/reference/android/app/PendingIntent) — identity, flags, and mutability.
- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — restoration boundaries.

Technically reviewed against these primary sources on 2026-10-13 by editorial review. The order route is illustrative.
