---
id: "MEM-08"
question: "Why can a Singleton holding Activity Context leak memory?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "A"
phase: 1
priority: "P1"
order: 63
editorial_status: "reviewed"
---

# MEM-08

## Original interview question

Why can a Singleton holding Activity Context leak memory?

## What the interviewer evaluates

- Explain lifetime mismatch and the retained Activity/view graph.
- Choose application context only for operations that do not require Activity capabilities or theme.
- Correct ownership instead of reflexively replacing every Context reference.

## Explanation in Arabic

الـsingleton غالبًا عايش طول عمر الـprocess. لو خزّن `Activity` كـContext، عمر الـActivity يقصر عند rotation أو إغلاق الشاشة، لكن المرجع من singleton يمنع GC من جمعها ومعاها view tree وresources. لو dependency محتاجة Context عام للملفات أو موارد لا تعتمد على theme، استخدم `applicationContext`. لكن `applicationContext` مش بديل سحري لكل حاجة: عرض dialog أو طلب Activity Result يحتاج Activity حية، والأصح تمررها وقت العملية أو تربط المكوّن بالـlifecycle المناسب. افحص retaining path للتأكد من leak الفعلي.

## Practical walkthrough

مثال image cache في `object` محتاجة تفتح cache directory: ادّيها `applicationContext` وقت الإنشاء، وما تخزنش `Activity`. لو محتاجة تعرض picker أو dialog، خليك في الـActivity نفسها وابعث للـcache النتيجة أو البيانات. بعد rotation مرتين، heap dump لازم ما يلاقيش الـActivity القديمة من cache root. كمان شوف أي lambda داخل cache لأنها ممكن تلتقط الـActivity حتى لو field اسمه Context سليم.

## Why it matters and how it works

A static or singleton field is reachable for the process lifetime. Storing a short-lived Activity there creates a strong path to the Activity and its views after recreation. Application context has process lifetime and is safe to retain for compatible APIs, but it lacks an Activity's window, lifecycle, and sometimes themed behavior. A singleton may also leak through a callback that captures `this`, even when its direct Context field looks harmless.

## Worked example

`object ImageCache { lateinit var context: Context }` initialized with `this` in an Activity retains that Activity. Instead, initialize a cache needing only file access with `applicationContext`, or inject an application-scoped Context via DI. If a picker must launch, keep the launcher in the Activity and pass a result into the cache; do not store the Activity in it. These snippets describe ownership, not a full compilable cache.

This Android sketch assumes a cache that only needs files, never UI theming or an Activity result. It has not been compiled in this repository.

```kotlin
import android.content.Context
import java.io.File

class ThumbnailDiskCache(context: Context) {
    private val appContext = context.applicationContext
    val directory: File
        get() = File(appContext.cacheDir, "thumbnails")
}
```

The caller still owns UI launchers and disposes any listeners it registers with this cache.

## Trade-offs and decision criteria

Application Context is appropriate for application-level resources and storage, but a UI operation requires an Activity-scoped owner. Passing a Context at call time may be simpler than making a global cache stateful. DI scope should match dependency lifetime. Avoid a weak Activity reference as the default fix; it can disappear at unpredictable times and hides bad ownership.

## Failure modes

Repeated rotation retains several Activities and grows heap. A singleton storing a View or lambda indirectly retains Activity even after replacing a Context field. Using application Context for a dialog can fail due to missing window token or wrong theme. Diagnose with LeakCanary or a heap dump and verify the retaining path is removed after the fix.

## Production perspective

For an image cache, inject only an application-scope directory or Context, set a bounded cache size, and keep UI callbacks outside the singleton. Test repeated rotation and navigation, then compare retained Activity counts. Review DI scopes so Activity-scoped dependencies do not flow into singletons.

## Interview answer — short

“A singleton can outlive an Activity. If it holds the Activity Context, that strong reference retains the destroyed Activity and its view tree. Use application Context for compatible app-scope work and keep UI owners short-lived.”

## Interview answer — structured

“The leak is a lifetime mismatch: the singleton remains reachable for the process, while an Activity should become collectible after it is destroyed. A field, callback, or captured lambda can keep that Activity alive. If the singleton only needs storage or application resources, I inject `applicationContext`. If the operation needs a window, theme, or lifecycle, I do it from a live Activity or pass a short-lived interface at call time. I verify by rotating the screen and inspecting a heap retaining path.”

## Interview answer — deep senior

“I reason about object ownership first. An application singleton is a GC root path for as long as the process lives. Putting an Activity Context in it can retain the Activity, its Views, drawables, and callbacks through configuration changes. The fix is to reduce the dependency's scope: an application Context for file/cache work, or an Activity-scoped component for UI work. I also inspect indirect captures such as a lambda registered with the singleton, because changing one field may leave the leak. I do not blindly replace every Context with application Context, since window and themed operations need a live Activity and can fail or behave incorrectly otherwise. A repeatable rotation test plus heap analysis demonstrates that old Activity instances become collectable after cleanup. In a file-backed thumbnail cache, the singleton can safely keep an application Context, but the picker launcher stays in the Activity. I inspect callback fields as well as the Context field, then rotate twice and check the old Activity's retaining path. This catches a lambda leak that a simple field replacement would miss.”

## How to answer in the interview

- **Why:** Tie singleton lifetime to the process.
- **How:** Inject application Context only for process-safe services.
- **Trade-off:** Application Context lacks Activity UI behavior.
- **Failure case:** A captured lambda can retain Activity despite field cleanup.
- **Production solution:** Keep picker ownership in Activity and verify rotation heap paths.

## Deep-dive talking points

Discuss scope mismatch, indirect lambda captures, application versus Activity Context, UI window ownership, and heap verification.

## Follow-up questions

- Is `applicationContext` suitable for showing a dialog? **Answer:** generally no; dialog UI needs an appropriate live window and Activity theme.
- Can a singleton leak an Activity without storing a Context field? **Answer:** yes; a listener or lambda capturing the Activity can form the same retaining path.
- How do you prove the fix? **Answer:** repeat navigation/rotation and inspect retained Activity paths in a heap dump or leak detector.

## Self-check rubric

Trace the singleton-to-Activity path, choose a correct scope, identify indirect capture, and verify collection after rotation.

## References and reviewed-on date

- [Memory leak patterns](https://developer.android.com/topic/performance/memory) — resource and reference ownership.
- [Context API](https://developer.android.com/reference/android/content/Context) — application and Activity context behavior.

Technically reviewed against these primary sources on 2026-10-13 by automated editorial review. The cache sketch is illustrative.
