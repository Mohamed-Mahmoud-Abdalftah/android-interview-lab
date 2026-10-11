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

An order-delivered notification targets `order/731`. Its content intent uses an explicit Activity, a unique order-specific request identity, and `FLAG_IMMUTABLE` plus the intended update flag. A parent stack leads from Order Detail to Orders. The destination validates the ID, checks the current account's authorization via repository, then renders loaded, missing, or sign-in states. Do not treat the ID in the Intent as authorization. Exact PendingIntent flags and NavHost routing should be integration-tested on supported API levels.

## Trade-offs and decision criteria

`TaskStackBuilder` is appropriate for a normal Activity hierarchy; a special isolated destination can use a separate-task pattern, but it changes Back expectations. Navigation libraries can synthesize an in-app destination stack when the app uses one host Activity. Immutable PendingIntents reduce tampering for fixed actions; mutable ones are needed only for specific fill-in use cases and require extra care. Stable IDs are safer than bundling a stale serialized Order.

## Failure modes

Two notifications share PendingIntent identity and both open the latest order. Back exits immediately instead of revealing the expected parent. A cold Activity reads a null singleton and crashes. A deleted order renders stale data. An implicit or mutable PendingIntent exposes an unnecessary injection surface. Test multiple simultaneous notifications, existing and killed process, signed-out return, deleted item, task switch, Back and Up on supported versions.

## Production perspective

Create a notification routing contract with explicit destination type and stable entity ID. Authorization and data loading happen after launch. Preserve any pending action only if it can safely resume after sign-in; otherwise route to a safe home screen. Instrument tap-to-destination success, missing-item outcome, and crash rate without sensitive payloads. A UI test kills the process before tapping two distinct order notifications and asserts correct ID and Back behavior.

## Interview answer — short

“I design notification taps as cold external launches: supply a stable destination ID, construct the expected back stack, validate authorization, and rebuild data after process death. PendingIntent identity and mutability must be deliberate.”

## Interview answer — structured

“For an ordinary destination I create a content PendingIntent and a parent stack, or configure the app's navigation graph to produce equivalent Back behavior. Each notification has a distinct identity so the system does not reuse stale extras. The launched screen accepts a stable ID and loads current data rather than depending on in-memory state. It handles signed-out and missing-item cases. I test multiple notifications, warm and cold launch, process recreation, and both Back and Up. The notification carries a stable destination ID, not a cached screen object or payment result. I make its PendingIntent explicit and immutable by default, distinguish simultaneous notifications by identity, and rebuild the expected parent stack. On cold start I authenticate and load current server state, including the case where the order was deleted.”
## Interview answer — deep senior

“A notification can outlive the process, the session, and even the underlying entity. I therefore treat it as an untrusted external route, not a shortcut into an existing ViewModel. The PendingIntent is explicit, uses the least mutability required, and has identity chosen so distinct notifications do not collide. I choose a normal parent stack or a special task based on product navigation expectations, then verify Back and Up after a cold launch. The route carries a small stable ID; a repository fetches current data and checks account authorization. If the session expired, sign-in or a safe destination takes over. I test pending intent reuse, two concurrent notifications, deleted data, process kill, and task switching, and monitor navigation failures after release. Notification taps can arrive into an existing task or a fresh process with no initialized ViewModel or singleton, so navigation must be reconstructable from a durable key. I choose a content Intent and TaskStackBuilder/deep-link strategy based on the expected Back behavior, and test both normal and special destinations. PendingIntent identity depends on action/data/component/request code rather than extras alone; two receipts can accidentally share one and open the latest order. I use distinct identities and minimal mutable surface. The destination checks current session and backend ownership before rendering sensitive details, then handles missing or stale records. Tests cover multiple notifications, logout, killed process, task reuse and Back navigation.”
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

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The order route is illustrative.
