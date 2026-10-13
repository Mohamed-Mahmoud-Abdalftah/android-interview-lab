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

## Practical walkthrough

لو singleton محتاج `Context` بس عشان `cacheDir`, الأفضل factory تستخرج `File` وتديها للcache؛ كده singleton ما يمسكش Context أصلًا. لو API تانية فعلًا محتاجة Context طول process، `applicationContext` مناسب بشرط ما تكونش window/themed UI capability. لا تدي singleton Activity أو View أو Dialog، لأن rotation/finish يسيبهم referenced. اطلب dependencies أضيق زي `Resources`؟ خليك حذر إن resources configuration ممكن تتغير؛ ما تحفظش themed object قديم. راجع constructor scope في DI، اعمل heap leak test، وخلي screen-specific target request له cancellation مع view lifecycle.

## Trade-offs and decision criteria

Application Context is a sensible default for truly process-scoped Android services, but a narrow `File` or `StorageGateway` is easier to test and reduces accidental capability use. Activity Context can be valid inside an Activity-scoped object, not a process singleton. A provider that owns an observer for the app lifetime needs an explicit shutdown policy, even if its Context lifetime is correct.

## Failure modes

`object Tracker { lateinit var activity: Activity }` retains every prior screen once replaced callbacks keep references. A listener registered with Application Context but never unregistered can accumulate duplicate events. A singleton caches a themed Drawable derived from an old Activity and displays wrong assets after dark-mode change. Find the GC-root path in a heap dump, remove long-lived UI references, and invalidate configuration-sensitive caches.

## Production perspective

For analytics, keep an application-scoped client with an injected transport and application-level storage capability. Screen lifecycle owners submit immutable events, never a Context or View reference. For a third-party SDK that insists on Activity for a one-time UI launch, wrap that call at the presentation boundary and do not let its process singleton retain the Activity. Rotate and close screens under LeakCanary/heap inspection and test listener registration counts.

## Interview answer — short

“I first ask what capability the singleton needs. For process-lifetime non-visual work I inject Application Context or, better, a narrower dependency such as a cache directory. I never retain Activity or View references in it, and I balance any registered listeners.”

## Interview answer — structured

A singleton outlives Activity recreation, so storing Activity Context keeps the old screen reachable and leaks its view tree. If the singleton needs files or another non-visual Android service, I inject Application Context or the exact service. UI needing a current theme or window stays in Activity scope. I also audit callbacks and caches because using Application Context alone does not prevent leaks, and I test repeated rotation and screen closure with a heap dump. For a process-scoped nonvisual dependency I inject Application Context, but I avoid keeping Activity, Dialog, View or themed Drawable in a singleton.

## Interview answer — deep senior

I treat the Context request as a dependency-design smell until I know the capability. A process singleton needing app-private storage can receive a directory or an Application Context; an SDK UI operation requiring Activity stays a short-lived presentation call. I never promote an Activity, Fragment, View, or window-themed resource into process scope. I audit any receiver, observer, Cursor, or callback registered by the singleton and define unregister or process-lifetime behavior explicitly. After rotation and locale/night-mode changes, I inspect heap paths for destroyed Activities and verify that cached resources are not tied to an obsolete visual configuration. A singleton stays reachable while its process lives, so any Activity reference it stores prevents that Activity and its view tree from being collected after rotation.

A disk cache constructor that only needs `cacheDir` should accept a `File`, which is simpler to test and cannot retain an Activity by accident. If a platform API requires Context for the lifetime of the process, Application Context is appropriate for a process-scoped singleton. A Dialog or view target still belongs to the current screen; passing Activity Context briefly there is correct, while storing it in the singleton is the leak. I inspect DI scopes and cancellation of screen requests, then use a heap dump or leak test across rotation. The dependency type should reveal the narrow capability required.

## How to answer in the interview

- **Why:** Singleton lifetime can exceed every Activity and view lifetime.
- **How:** Identify the exact capability: cache directory, service, or themed window UI.
- **Trade-offs:** Inject a `File` or narrow service before accepting a broad Context dependency.
- **Failure cases:** Name retained Activity/View and stale themed resources.
- **Production solution:** Build an application-scoped disk cache with cancellable view requests.

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

Technically reviewed against these primary sources on 2026-10-13 by editorial review. The singleton example is architectural and was not instrumented on a device.
