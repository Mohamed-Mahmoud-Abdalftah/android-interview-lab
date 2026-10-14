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

## Explanation in Arabic

الـ Configuration Changes وما الذي ينجو منها (What survives them) هو أساس فهم استقرار التطبيقات أثناء التدوير وتغيير إعدادات الجهاز:

1. ما هي الـ Configuration Changes؟
   - هي أحداث تحدث على مستوى نظام التشغيل تؤدي إلى تغيير في بيئة تشغيل التطبيق (Runtime Configuration).
   - أشهر الأمثلة:
     * تدوير الشاشة (Screen Orientation: Portrait <-> Landscape).
     * تغيير لغة الجهاز (Locale Change: Arabic <-> English).
     * تبديل الوضع الليلي (Dark Mode / Night Mode toggle).
     * الدخول والخروج من وضع تقسيم الشاشة (Multi-window / Split-screen).
     * تغيير حجم الخط وحجم العرض (Font Scale / Display Density).

2. ما الذي يفعله نظام أندرويد تلقائياً؟
   - النظام يقوم بـ **تدمير الـ Activity الحالية بالكامل (`onDestroy`) وإعادة إنشائها من الصفر (`onCreate`)** حتى يقوم بإعادة تحميل الموارد الملائمة (مثل ملفات `layout-land`, `values-ar`, `values-night`).

3. ما الذي ينجو من هذا التدمير (What survives)?
   - **الـ ViewModel:** ينجو تماماً في الذاكرة بفضل `ViewModelStore`.
   - **الـ SavedInstanceState Bundle:** ينجو ويحفظ الحقول الأساسية والنصوص المكتوبة في الـ EditTexts تلقائياً.
   - **الـ Application Singleton / Process Memory:** يظل حياً كما هو لأن الـ Process نفسه لم يمت.

## Practical walkthrough

ما الذي يضيع وما الذي ينجو عند تدوير الشاشة في تطبيق عملي:
- **ما يضيع (Destroyed & Lost):**
  * كائن الـ Activity القديم، والـ Views، والـ Fragments القديمة.
  * أي كود معلق في `lifecycleScope.launch` يتم إلغاؤه فوراً.
- **ما ينجو (Survives):**
  * الـ ViewModel وكافة الـ StateFlows المخزنة بداخله؛ تظل تعمل وتستلمها الـ Activity الجديدة فوراً.
  * نصوص حقول الإدخال إذا كان لها `android:id` محدد في الـ XML.
  * الـ Background Coroutines التي تعمل في `viewModelScope` تستمر بدون انقطاع.

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

Configuration changes (screen rotation, dark mode, locale, multi-window) cause Android to completely destroy and recreate the Activity to reload resources. The ViewModel survives in memory via ViewModelStore, the saved instance state Bundle survives for UI state, and the app process remains intact.

## Interview answer — structured

A configuration change occurs when device hardware or system settings change at runtime, altering the active resource configuration.

Common configuration changes include.

First, screen orientation changes (portrait vs landscape). Next, system dark mode toggles (day vs night theme).
Locale/language changes. Multi-window resizing and folding/unfolding of foldable devices.
Finally, font scaling and display density modifications.

By default, Android destroys and recreates the entire Activity (`onPause -> onStop -> onDestroy` followed by `onCreate -> onStart -> onResume`) so the app can load new resources (e.g., `layout-land` or `values-night`).

**What survives:**

First, a ViewModel is retained in memory by the `ViewModelStore`, preserving ongoing business logic and `viewModelScope` coroutines. Next, saved Instance State (`onSaveInstanceState` / `SavedStateHandle`) serializes small UI states across recreation.
Finally, with Process Memory, singletons, Hilt graph, and memory caches remain intact because the Linux process never died.


## Interview answer — deep senior

Under the hood, why does Android destroy the Activity rather than just swapping Views?

Because swapping themes and layouts dynamically on an existing Activity would require manually traversing every drawable, style attribute, dimension, and string resource across the entire view tree. Recreating the Activity provides a clean slate where all resources are cleanly rebound from APK asset tables.

While developers can declare `android:configChanges="orientation|screenSize"` in the Manifest to prevent recreation, Google strongly discourages this. It forces you to manually override `onConfigurationChanged()` and update every layout, font, and padding by hand, almost always leading to visual bugs and broken accessibility.


## How to answer in the interview

- **Why:** The system can recreate UI for resource/configuration changes.
- **How:** Distinguish new Activity/views from retained scoped ViewModel and saved small keys.
- **Trade-offs:** Put transient UI position in saved state, durable draft data in storage.
- **Failure cases:** Mention stale Activity references and oversized Bundles.
- **Production solution:** Restore a search query, reload results, and test rotation during loading.

## Deep-dive talking points

Discuss Activity recreation versus manual configuration handling, resource qualifier selection, ViewModelStore ownership, saved-state size/timing, and why an external operation requires durable identity. Explain how a recreation test differs from a process-death test.

## Follow-up questions

- **Interviewer:** "Why do EditTexts automatically restore their text across rotation?"
  **Answer:** "Because standard Android framework Views implement `onSaveInstanceState()`. If the View has a unique `android:id` assigned, the framework automatically serializes its input text and scroll state into the instance state Bundle and restores it upon recreation."

- **Interviewer:** "How does `rememberSaveable` in Jetpack Compose survive configuration changes?"
  **Answer:** "`rememberSaveable` registers with Compose's `SaveableStateRegistry`, which hooks into Android's `onSaveInstanceState` Bundle mechanism under the hood."

- **Interviewer:** "Can a non-configuration instance be retained manually without ViewModel?"
  **Answer:** "Historically yes, via `onRetainCustomNonConfigurationInstance()`, but this is deprecated in favor of Jetpack ViewModel, which provides the standardized, type-safe implementation of this exact mechanism."

## Self-check rubric

Explain one configuration change and its recreation effect; name what a ViewModel, saved state, and durable store each preserve; identify a stale Activity reference; design a checkout restoration path; and distinguish process-death testing from rotation testing.

## References and reviewed-on date

- [Activity lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle) — Activity recreation and process state.
- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — saved-state boundaries and size guidance.
- [ViewModel overview](https://developer.android.com/topic/libraries/architecture/viewmodel) — scope and configuration retention.

Technically reviewed against primary documentation on 2026-10-13.
