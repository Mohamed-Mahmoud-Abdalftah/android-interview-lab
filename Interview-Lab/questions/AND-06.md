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

Configuration changes represent environmental, hardware, or system-level setting modifications that occur while an Android application is running, forcing the operating system to recalculate its active resource configuration. Common triggers include screen orientation changes between portrait and landscape, system language or locale switching, toggling between light and dark display modes, multi-window mode entry and split-screen resizing, device folding or unfolding on foldable hardware, and dynamic font scale or display density adjustments.

When a configuration change occurs, Android's default architectural behavior is to destroy the active Activity instance through its teardown lifecycle callbacks from onPause through onStop to onDestroy, and immediately recreate a fresh Activity instance from onCreate through onStart to onResume. This destructive recreation cycle is deliberate: it allows the framework to automatically reload resources matching the updated configuration qualifiers from the application package, such as layout-land, values-night, or values-ar.

Understanding what survives this recreation is fundamental to building reliable mobile software. First, Jetpack ViewModels survive intact in process memory because they are retained by the ViewModelStoreOwner across the configuration boundary, preserving ongoing business logic and viewModelScope coroutines. Second, lightweight UI state survives via the SavedStateHandle or onSaveInstanceState Bundle, which serializes key-value pairs across the recreation boundary. Third, application-level singletons, static fields, in-memory caches, and dependency injection graphs remain untouched in the Android Runtime heap because the underlying Linux operating system process is never terminated. Conversely, the old Activity instance, its View hierarchy, Fragments, dialogs, and any coroutines launched inside the unmanaged lifecycleScope are completely destroyed and garbage collected.

## Practical walkthrough (English)

In a production ecommerce checkout screen, consider what happens when a customer rotates their tablet while completing a payment form:
1. What is destroyed and lost:
The active Activity instance, inflated ViewBinding hierarchies, and Dialogs are destroyed immediately. Any asynchronous tasks launched inside lifecycleScope are canceled as the lifecycle transitions to DESTROYED. Local Activity instance variables, such as temporary boolean flags or unsaved input text not backed by persistent IDs, are dropped from memory.
2. What survives and persists:
The CheckoutViewModel and its StateFlow subscriptions remain uninterrupted in heap memory via the ViewModelStore. Ongoing payment processing coroutines running inside viewModelScope continue execution without interruption. If input fields possess unique android:id attributes, their entered text is automatically serialized into the instance state Bundle and restored into the newly inflated layout.
3. Failure scenario:
If an engineer stores an order submission state in an Activity member variable or launches the payment network request in lifecycleScope, screen rotation cancels the request mid-flight while leaving the user on a blank form. If the user taps submit again upon recreation, duplicate charges or conflicting database records occur. The architectural safeguard is to execute all transactions within viewModelScope, track operation identifiers through SavedStateHandle, and query backend payment status before retrying.

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

A configuration change occurs when runtime environment settings change, such as screen rotation, dark mode switching, or locale adjustments. By default, Android completely destroys and recreates the Activity to reload qualifier-matching resources. The ViewModel survives in memory via ViewModelStore, the saved instance state Bundle preserves transient UI keys, and the Linux process remains alive.

## Interview answer — structured

A configuration change occurs when runtime environment variables change, such as device rotation, system language switching, dark mode toggling, or multi-window resizing. Android handles this by destroying the current Activity instance through its lifecycle callbacks and instantiating a fresh one to re-resolve qualifier-specific resources from the APK asset table.

The system cleanly separates what is destroyed from what survives. The previous Activity instance, its View tree, and any jobs scoped strictly to the UI lifecycle are destroyed. However, the ViewModel survives continuously in process memory because it is retained by the ViewModelStoreOwner, ensuring that viewModelScope coroutines and business state remain uninterrupted.

Transient UI properties like scroll offsets and form inputs survive via SavedStateHandle or the onSaveInstanceState Bundle. Meanwhile, application-level singletons, network clients, and database handles stay alive because the underlying Linux process is never terminated during an ordinary configuration change.

In production, we avoid using android:configChanges to bypass recreation. Instead, we embrace the recreation cycle, delegate business operations to ViewModelScope, and persist critical transaction identifiers into durable storage, guaranteeing flawless state continuity.


## Interview answer — deep senior

At the operating system and Android Runtime level, configuration changes are orchestrated by the ActivityTaskManagerService in the system_server process. When a hardware sensor triggers a display rotation or the user toggles dark mode, the system server evaluates the delta between the device's current Configuration and the Activity's override configuration.

Rather than attempting an in-place mutation of the entire view hierarchy, Android intentionally destroys the Activity. Mutating an existing view tree in-place would require traversing every view, drawable cache, dynamic layout parameter, and dimension resource, which is historically error-prone and invites subtle layout corruption. By invoking performDestroy() followed by performCreate(), the ActivityThread binds a newly configured ResourcesImpl instance to the fresh Activity context, ensuring all layout and drawable inflations pull the exact qualifiers for the new environment.

The survival of the ViewModel across this destruction is managed by the NonConfigurationInstances record. Before the old Activity is destroyed, the framework invokes retainNonConfigurationInstances(), caching the ViewModelStore inside a platform holder in the ActivityClientRecord. When the ActivityThread constructs the new Activity instance, it supplies this cached record back via attach(), allowing the ViewModelProvider to retrieve the identical ViewModel instances from the existing store without executing their onCleared() callback.

Crucially, Staff engineers distinguish between configuration changes and process death. A configuration change preserves the entire JVM heap, including static variables, Dagger or Hilt singleton component graphs, and active background threads. Process death, triggered by the Linux kernel Low Memory Killer daemon, obliterates the process address space entirely. Attempting to bypass configuration recreation by declaring android:configChanges in the manifest transfers the entire burden of manual resource updates onto the developer via onConfigurationChanged(), which frequently breaks accessibility scaling, locale switching, and foldable posture transitions.

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
