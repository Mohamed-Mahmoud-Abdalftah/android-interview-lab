---
id: "AND-06"
question: "What are configuration changes, and what survives them?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "A"
phase: 1
priority: "P1"
order: 36
editorial_status: "reviewed"
---

# AND-06

## Original interview question

What are configuration changes, and what survives them?

## What the interviewer evaluates

- Distinguish recreation of an Activity instance from death of the app process.
- Place transient screen state, small restorable state, and durable data in the right owners.
- Test rotation, resizing, locale changes, and night mode without assuming a particular callback order is a persistence contract.

## Concept and technical explanation

A configuration change alters the environment used to select resources, such as locale, night mode, orientation, font scale or window size. By default Android recreates an Activity for many such changes; a manifest `configChanges` declaration or other handling can change the path, so “always destroyed” is inaccurate. In an ordinary recreation within the same process, a correctly scoped ViewModel is retained across the new Activity instance; the old Activity and its view tree are replaced. Saved state can reconstruct small UI values, and durable storage holds data that must survive process death or complete dismissal. Neither view text restoration nor `viewModelScope` continuation is an unconditional transaction guarantee. External operations need durable identity and idempotency.

## Practical walkthrough (English)

Consider rotating a checkout screen while a payment request may be in flight:
1. Expect a new Activity and views under default configuration handling, but check the manifest and host behavior.
2. A correctly scoped ViewModel can keep UI state during ordinary in-process recreation. A UI collector tied to the old Activity/view ends and the new screen collects again.
3. Save small reconstruction inputs, such as a draft or operation ID, with saved state when appropriate. Persist a payment attempt ID durably before depending on it.
4. On recreation, query authoritative server status before offering a retry. `viewModelScope` alone does not make a payment transaction exactly once; backend idempotency is required.
5. Test rotation, locale/night mode, process recreation and screen dismissal separately. The system View state save path depends on IDs, widget behavior and the activity's save/restore path.

## Explanation in Arabic

Configuration change يعني إعدادات بتحدد resources وطريقة عرض الشاشة اتغيرت، زي اللغة، الوضع الليلي، اتجاه الجهاز، حجم الخط أو مساحة النافذة. في الإعداد المعتاد Android يعيد إنشاء الـ Activity عشان يحمل الموارد المناسبة. لكن `android:configChanges` أو تعامل خاص ممكن يغير المسار؛ لذلك مش كل تغيير معناه هدم تلقائي بنفس ترتيب callbacks.

لو حصلت إعادة إنشاء عادية والـ process لسه شغالة، الـ Activity والـ Views القديمة تتبدل. ViewModel مرتبطة بالـ owner الصحيح تفضل في الذاكرة وتوصل للنسخة الجديدة، لكن reference للـ Activity القديمة لازم ما تتخزنش داخلها. وظائف UI المربوطة بعمر الشاشة القديمة تنتهي، والجمع يبدأ من جديد مع الشاشة الجديدة. Saved State يساعد في قيم صغيرة قابلة للاستعادة؛ مش كل `EditText` مضمون يرجع لمجرد وجود `android:id`، لأن مسار الحفظ ونوع الـ View والتعامل مع الحالة يفرقوا.

العملية الخارجية زي الدفع لها حدود أخرى. استمرار coroutine في `viewModelScope` أثناء تدوير عادي لا يضمن عدم تكرار طلب دفع أو بقاء العملية بعد موت الـ process. احفظ معرف المحاولة في مخزن دائم واتبع عقد idempotency مع السيرفر، ثم استعلم عن حالة الطلب بعد إعادة الإنشاء. اختبر rotation وresize واللغة والوضع الليلي وقت تحميل الشاشة، واختبر process death منفصل.

## Practical walkthrough

شاشة بحث عند التدوير:
- الـ Activity القديمة تتبدل افتراضياً، والـ ViewModel المرتبطة بمالكها تكمل داخل نفس الـ process.
- خزّن query صغيرة في `SavedStateHandle` أو حالة saveable لو لازم ترجع بعد إعادة إنشاء النظام، وحمّل النتائج من repository.
- الـ collector القديم المربوط بالـ Activity ينتهي؛ النسخة الجديدة تشترك وتعرض أحدث state.

ولو الشاشة شاشة دفع، احفظ `paymentAttemptId` في تخزين دائم قبل الطلب، واستخدم idempotency key، وبعد العودة اسأل السيرفر عن الحالة قبل إعادة POST. ما تعتمدش على `onSaveInstanceState` كسجل معاملات.

## Why it matters and how it works

Android can destroy the current Activity and create a new instance with resources matching the new configuration. A ViewModel scoped to the retained ViewModelStoreOwner survives an ordinary configuration recreation, but Activity fields, view references, and unowned jobs do not. `SavedStateHandle` or `rememberSaveable` stores a small serializable reconstruction key across eligible system-initiated recreation; Room or another durable store owns data that must outlive a task or process. The saved-state callback is not a transaction log and is not guaranteed for every exit path.

## Worked example

In a search screen, keep the current query in `SavedStateHandle`, derive results from a repository, and collect UI state with the lifecycle. The ViewModel is recreated with the saved query after eligible process restoration; the repository reloads results. This is illustrative Android code with Lifecycle and ViewModel SavedState dependencies and an application-provided `SearchRepository`.

```kotlin
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class SearchViewModel(
    private val savedState: SavedStateHandle,
    private val repository: SearchRepository
) : ViewModel() {
    private val mutableResults = MutableStateFlow<List<SearchResult>>(emptyList())
    val results = mutableResults.asStateFlow()
    val query: String get() = savedState["query"] ?: ""

    fun search(value: String) {
        savedState["query"] = value
        viewModelScope.launch { mutableResults.value = repository.search(value) }
    }
}
```

The surrounding app supplies `SearchRepository` and `SearchResult`; competing searches need cancellation or `flatMapLatest` if stale results are possible. The example illustrates ownership, not a complete search feature.

## Trade-offs and decision criteria

Retaining a ViewModel avoids needless reloads and preserves screen logic during rotation, but it consumes memory and cannot survive process death. Saved state is suitable for small reconstruction inputs, not large lists or bitmaps. Durable storage costs I/O but is appropriate for user data and operation records. Opting out of Activity recreation with `configChanges` shifts resource updating onto the app and is rarely a substitute for correct state ownership.

## Failure modes

A developer stores a payment attempt only in an Activity field; rotation loses the attempt and a new screen sends a second charge. Persist the attempt ID and ask the backend for its status before retrying. Another failure is retaining the old Activity in a ViewModel or singleton, leaking views and resources across recreation. Holding a bitmap in saved state can also create oversized Bundles and slow restoration.

## Production perspective

For a checkout screen, persist the server operation ID and user-entered draft separately. On recreation, render the draft from saved state and rehydrate payment state from the persisted operation and server. Instrument recreation tests with rotation, locale/night mode, and background process termination. Trace duplicate submissions and state restoration failures by operation ID without logging payment credentials.

## Interview answer — short

Configuration changes alter resources or display conditions. Android recreates an Activity by default for many of them, while the process and a correctly scoped ViewModel normally remain. The old views and Activity references are replaced; saved state restores small eligible values and durable storage holds business data. A handled configuration may follow another path, so verify the host behavior.

## Interview answer — structured

Rotation, locale, night mode and window resizing can change the resource configuration. Under default handling, Android destroys and recreates the Activity so the new instance loads matching resources. The process usually stays alive, and a ViewModel scoped to the retained owner survives that ordinary configuration recreation. The old Activity and views are not reusable, and UI collection should be tied to their lifecycle and re-established by the new screen. `onSaveInstanceState`, `SavedStateHandle` or Compose saveable state can restore small UI values, but saved state is conditional and not a database. Framework views may restore their own state when they participate correctly; a unique ID alone is not a universal guarantee. Some apps handle specific changes through `configChanges`, which requires updating configuration-sensitive UI themselves. For checkout, I retain a small operation ID but persist payment identity durably, then reconcile with the server after recreation. A continuing ViewModel coroutine is not an exactly-once payment contract. I test configuration recreation separately from system process death and user dismissal.

## Interview answer — deep senior

A configuration change is a change in the environment used for resource selection or visual behavior, not a synonym for rotation alone. Locale, night mode, font scale, density and window bounds are examples. For many changes, the default Android path recreates the Activity: a new instance receives the new configuration and inflates new views. If the app declares `android:configChanges` for a particular change, it accepts responsibility for handling that change without the default recreation. Therefore I describe the normal path and inspect the manifest rather than claiming a universal callback order.

During ordinary configuration recreation, the process stays alive. A ViewModel associated with the retained `ViewModelStoreOwner` can be reused by the new Activity instance, and its `viewModelScope` work may continue while that owner remains. This does not justify storing the old Activity or ViewBinding in the ViewModel; those references belong to the old view lifetime. A lifecycle-scoped UI collector ends with its old owner and the new screen collects again. Saved-state APIs preserve compact reconstruction values under their documented conditions. Some Views have built-in state restoration, but it depends on their save/restore behavior and configuration, not simply on assigning an ID. Large data or financial transaction status belongs in durable local/server storage.

Suppose checkout rotation occurs while a network response is uncertain. A ViewModel can keep a loading state through this one recreation, but process death or an app restart removes that memory. I persist an operation identity before submission, use a server idempotency key and query status before retrying. That protects correctness more than moving the HTTP call from `lifecycleScope` to `viewModelScope` alone. In production I exercise rotation, resize, locale/night-mode switch, process recreation and leaving the destination separately. I inspect the resulting resource configuration and state transitions rather than treating `onSaveInstanceState` as a transaction log.

## How to answer in the interview

- **Why:** The system can recreate UI for resource/configuration changes.
- **How:** Distinguish new Activity/views from retained scoped ViewModel and saved small keys.
- **Trade-offs:** Put transient UI position in saved state, durable draft data in storage.
- **Failure cases:** Mention stale Activity references and oversized Bundles.
- **Production solution:** Restore a search query, reload results, and test rotation during loading.

## Deep-dive talking points

Discuss Activity recreation versus manual configuration handling, resource qualifier selection, ViewModelStore ownership, saved-state size/timing, and why an external operation requires durable identity. Explain how a recreation test differs from a process-death test.

## Follow-up questions

- **Interviewer:** "Does a ViewModel always survive a configuration change?"
  **Answer:** "A correctly scoped ViewModel is retained across an ordinary in-process recreation while its owner remains. A custom handling path or owner removal changes the story; it does not survive process death."
- **Interviewer:** "Does giving an EditText an ID guarantee restored text?"
  **Answer:** "No. The View must participate in the save/restore path, and the Activity's lifecycle must provide saved state. I test the actual widget and host."

## Self-check rubric

Explain one configuration change and its recreation effect; name what a ViewModel, saved state, and durable store each preserve; identify a stale Activity reference; design a checkout restoration path; and distinguish process-death testing from rotation testing.

## References and reviewed-on date

- [Activity lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle) — default recreation and process distinction.
- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — ViewModel, saved-state and durable-storage boundaries.
- [ViewModel overview](https://developer.android.com/topic/libraries/architecture/viewmodel) — owner and configuration lifetime.

Technically reviewed against primary documentation on 2026-10-19.
