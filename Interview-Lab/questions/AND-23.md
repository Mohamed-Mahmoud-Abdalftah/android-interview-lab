---
id: "AND-23"
question: "A Singleton needs a Context. How do you choose the correct lifecycle and prevent a leak?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "C"
phase: 1
priority: "P1"
order: 53
editorial_status: "reviewed"
---

# AND-23

## Original interview question

A Singleton needs a Context. How do you choose the correct lifecycle and prevent a leak?

## What the interviewer evaluates

- Challenge whether the singleton actually needs Context or a narrower capability.
- Match a process-lifetime dependency with Application Context, not a screen Activity.
- Consider configuration-sensitive resources and cleanup of registered callbacks.

## Explanation in Arabic

أول سؤال: الـsingleton محتاج `Context` ليه؟ لو محتاج مكان ملفات أو `ContentResolver` مثلًا، مرّر له `applicationContext` أو interface أصغر يقدّم الحاجة المطلوبة. ما تخزنش Activity Context في field طويل العمر: بعد rotation الـsingleton يفضل ماسك Activity القديمة وكل view graph، وده leak. لكن ما تستخدمش Application Context لأي UI: Dialog أو inflate بيعتمد على theme/window لازم يتعمل في screen scope. ولو singleton سجّل callback أو receiver، لازم يكون له ownership واضح وطريقة unregister؛ تغيير Context وحده مش كفاية.

## Why it matters and how it works

A singleton remains reachable for the app process. Any Activity stored in it remains reachable as well even after that Activity should be destroyed. Application Context has compatible process lifetime for non-visual operations. But a singleton may still leak listeners, Cursors, or view callbacks regardless of which Context it holds. Visual configuration belongs to the current window, so passing Application Context into UI rendering can produce stale or incorrect resources on multi-window and foldable devices.

## Worked example

A disk cache factory accepts an Application Context, immediately derives `cacheDir`, and retains only a `File` handle and its own bounded cache state. A screen-specific image loader call receives the current view target for one request and cancels it when the view ends. If the cache only needs `cacheDir`, inject that directory instead of retaining Context at all. This design example deliberately avoids a broad singleton field of type `Activity` or `View`.

## Trade-offs and decision criteria

Application Context is a sensible default for truly process-scoped Android services, but a narrow `File` or `StorageGateway` is easier to test and reduces accidental capability use. Activity Context can be valid inside an Activity-scoped object, not a process singleton. A provider that owns an observer for the app lifetime needs an explicit shutdown policy, even if its Context lifetime is correct.

## Failure modes

`object Tracker { lateinit var activity: Activity }` retains every prior screen once replaced callbacks keep references. A listener registered with Application Context but never unregistered can accumulate duplicate events. A singleton caches a themed Drawable derived from an old Activity and displays wrong assets after dark-mode change. Find the GC-root path in a heap dump, remove long-lived UI references, and invalidate configuration-sensitive caches.

## Production perspective

For analytics, keep an application-scoped client with an injected transport and application-level storage capability. Screen lifecycle owners submit immutable events, never a Context or View reference. For a third-party SDK that insists on Activity for a one-time UI launch, wrap that call at the presentation boundary and do not let its process singleton retain the Activity. Rotate and close screens under LeakCanary/heap inspection and test listener registration counts.

## Interview answer — short

“I first ask what capability the singleton needs. For process-lifetime non-visual work I inject Application Context or, better, a narrower dependency such as a cache directory. I never retain Activity or View references in it, and I balance any registered listeners.”

## Interview answer — structured

“A singleton outlives Activity recreation, so storing Activity Context keeps the old screen reachable and leaks its view tree. If the singleton needs files or another non-visual Android service, I inject Application Context or the exact service. UI needing a current theme or window stays in Activity scope. I also audit callbacks and caches because using Application Context alone does not prevent leaks, and I test repeated rotation and screen closure with a heap dump. For a process-scoped nonvisual dependency I inject Application Context, but I avoid keeping Activity, Dialog, View or themed Drawable in a singleton. UI work gets the current Activity for the duration of the call. I also unregister listeners and close Cursors; Application Context alone does not make a singleton leak-free.”
## Interview answer — deep senior

“I treat the Context request as a dependency-design smell until I know the capability. A process singleton needing app-private storage can receive a directory or an Application Context; an SDK UI operation requiring Activity stays a short-lived presentation call. I never promote an Activity, Fragment, View, or window-themed resource into process scope. I audit any receiver, observer, Cursor, or callback registered by the singleton and define unregister or process-lifetime behavior explicitly. After rotation and locale/night-mode changes, I inspect heap paths for destroyed Activities and verify that cached resources are not tied to an obsolete visual configuration. A singleton stays reachable while its process lives, so any Activity reference it stores prevents that Activity and its view tree from being collected after rotation. Application Context has a compatible lifetime for database, files or process-wide services, but is not the right owner for window-attached UI and may carry the wrong visual configuration. I pass a short-lived Activity through a function boundary when showing a dialog and clear callbacks when its lifecycle ends. I inspect heap dumps for the GC-root path instead of assuming every Context leak has the same cause. I test rotation and dark-mode changes to catch both retention and stale themed resources.”
## Deep-dive talking points

Explain GC-root reachability, process versus screen lifetime, narrow dependency injection, visual resource configuration, listener ownership, and testing leaks under repeated recreation.

## Follow-up questions

- [AND-04](../and-04/): Why is Application Context often safer for a disk cache? **Answer:** its lifetime matches a process-scoped cache and it is not tied to one Activity's views.
- [MEM-08](../mem-08/): Does replacing Activity Context fix every leak? **Answer:** no; callbacks or cached Views can still retain the screen.
- [AND-05](../and-05/): Can the singleton show a Dialog with Application Context? **Answer:** not as a substitute for a current visual owner and window token; keep dialog creation in screen scope.

## Self-check rubric

Identify the actual Context capability; show a safe process-scoped dependency; trace an Activity leak; give one non-Context leak path; and explain how to test configuration-sensitive cache behavior.

## References and reviewed-on date

- [Context API reference](https://developer.android.com/reference/android/content/Context) — Context lifetime and visual configuration.
- [Activity lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle) — Activity recreation.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The singleton example is architectural and was not instrumented on a device.
