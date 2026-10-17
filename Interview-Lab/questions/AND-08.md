---
id: "AND-08"
question: "What is ViewModel, and when is it cleared?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "A"
phase: 1
priority: "P1"
order: 38
editorial_status: "reviewed"
---

# AND-08

## Original interview question

What is ViewModel, and when is it cleared?

## What the interviewer evaluates

- Identify a ViewModel as a screen-level state holder scoped to a `ViewModelStoreOwner`.
- Distinguish configuration retention from process persistence.
- Choose the correct owner and avoid retaining Activity, View, or Fragment references in a longer-lived object.

## Concept and technical explanation

The Jetpack ViewModel is a specialized architectural component designed to store and manage UI-related data in a lifecycle-conscious manner, decoupling presentation state and business logic from UI controllers such as Activities and Fragments. Its primary architectural value is configuration resilience: because it is retained in memory across Activity recreations, it eliminates redundant network requests, database re-queries, and expensive data recomputations caused by screen rotation, dark mode switching, or window resizing.

A ViewModel's retention and disposal are dictated by its associated ViewModelStoreOwner. The owner supplies a ViewModelStore—an in-memory dictionary mapping ViewModel class keys to ViewModel instances. During a configuration change, the framework transfers this ViewModelStore from the dying Activity instance to the newly instantiated Activity instance via non-configuration token retention in ActivityThread. Consequently, the ViewModel instance remains undisturbed on the JVM heap.

The ViewModel's terminal lifecycle callback is onCleared(). This method is invoked exclusively when the host ViewModelStoreOwner reaches the end of its lifecycle and is permanently destroyed without recreation. Key triggers include: the user finishing an Activity by pressing the back gesture or calling finish(); a Fragment being permanently detached and popped from the FragmentManager backstack; or a Jetpack Compose navigation destination being popped from the NavBackStackEntry. When onCleared() is invoked, the framework automatically cancels the associated viewModelScope, stopping all active child coroutines and freeing asynchronous resources, after which the ViewModel instance becomes eligible for garbage collection.

## Practical walkthrough (English)

Examining the ViewModel clearing lifecycle in a real-time messaging application:
```kotlin
class ChatViewModel(
    private val chatSocket: ChatSocketManager,
    private val repository: MessageRepository
) : ViewModel() {

    init {
        // Connect to the WebSocket when ViewModel is created
        chatSocket.connect()
    }

    fun sendMessage(text: String) {
        viewModelScope.launch {
            repository.dispatchMessage(text)
        }
    }

    override fun onCleared() {
        super.onCleared()
        // onCleared is invoked only when the screen is permanently destroyed
        chatSocket.disconnect()
    }
}
```
Lifecycle behavior during user interaction:
1. When the user rotates the device, the host Activity is destroyed and recreated. The ChatViewModel is retained by the ViewModelStore, the WebSocket connection remains uninterrupted, and onCleared() is NOT called.
2. If the user navigates to an image preview and returns, the ChatViewModel persists in memory.
3. When the user presses the Back button or leaves the chat screen permanently, the host Activity finishes (isFinishing == true). The framework clears the ViewModelStore, cancels all jobs running in viewModelScope, and invokes onCleared(), disconnecting the socket cleanly and preventing thread leaks.

## Explanation in Arabic

الـ `ViewModel` في Android Jetpack هو حجر الأساس لإدارة الحالة، وفهم توقيت استدعاء `onCleared()` بدقة يمنع تسريب الموارد:

1. ما هو الـ ViewModel؟
   - هو فئة مصممة لتخزين وإدارة البيانات المرتبطة بواجهة المستخدم (UI-related data) بطريقة **تتحمل تدوير الشاشة (Lifecycle-conscious)**.
   - يفصل الـ Business Logic وتجهيز البيانات عن الـ Activity والـ Fragment.

2. أين يتم تخزينه وكيف ينجو من التدوير؟
   - يتم تخزينه داخل **`ViewModelStore`** يمتلكه الـ `ViewModelStoreOwner` (مثل الـ Activity أو Fragment).
   - عند تدوير الشاشة، النظام يدمر الـ Activity القديمة، ولكن الـ `ViewModelStore` يتم تمريره للـ Activity الجديدة بدون مساس، فيظل الـ ViewModel كما هو في الـ Heap.

3. متى يتم مسحه واستدعاء `onCleared()` تحديداً؟
   - يتم استدعاء `onCleared()` **فقط عندما تنتهي الشاشة نهائياً ولا تعود أبداً (Permanently Finished)**:
     * عندما يضغط المستخدم زر الرجوع (Back) وتنتهي الـ Activity (`activity.isFinishing == true`).
     * عندما يتم حذف الـ Fragment نهائياً من الـ FragmentManager بدون وضعه في الـ Backstack.
     * عندما تنتهي وجهة الـ Navigation في Jetpack Compose ويتم إخراجها من الـ NavBackStackEntry.
   - عند استدعاء `onCleared()`: يتم إلغاء الـ `viewModelScope` تلقائياً وإلغاء كافة الـ Coroutines التابعة له.

## Practical walkthrough

دورة حياة الـ ViewModel في الكود:
```kotlin
class ChatViewModel(private val chatSocket: ChatSocket) : ViewModel() {
    init {
        // 1. يبدأ الاتصال بالـ Socket:
        chatSocket.connect()
    }

    override fun onCleared() {
        super.onCleared()
        // 2. onCleared تستدعى فقط عند مغادرة الشاشة نهائياً:
        chatSocket.disconnect() // تنظيف المقابس والموارد غير المدارة
        Log.d("ChatVM", "ViewModel cleared permanently!")
    }
}
```
لو دور المستخدم الشاشة 100 مرة: `onCleared()` لن تستدعى ولا مرة! ستستدعى مرة واحدة فقط عندما يضغط المستخدم 'Back' ويغادر شاشة المحادثة.

## Why it matters and how it works

The owner supplies a `ViewModelStore`. Looking up a ViewModel by key returns the existing instance while that store remains valid, even if a configuration change replaces the UI object. The instance is cleared when the owner is permanently destroyed or its navigation back-stack entry is removed. `viewModelScope` follows that clearing boundary. This gives UI business logic a stable home without coupling it to one Activity instance, but it is still memory state and disappears on process death.

## Worked example

An order screen ViewModel exposes a `StateFlow<OrderUiState>` and loads by a stable `orderId`; the Activity collects it only while started. On rotation the ViewModel remains, and the new Activity subscribes. After process death a new ViewModel uses the saved `orderId` to reload from the repository. The implementation should inject a repository and `SavedStateHandle`; it must not keep the old Activity or binding. This is a lifecycle design example rather than a stand-alone compiled program.

## Trade-offs and decision criteria

Activity scope can share state across destinations but may retain too much data; destination scope gives cleaner isolation and clearing. A plain state holder may be sufficient for local Compose UI state, while a ViewModel fits screen business logic. Keep durable records in a repository and small restoration keys in saved state. A ViewModel does not replace `rememberSaveable`, Room, or lifecycle-aware collection.

## Failure modes

Scoping a shared ViewModel to the whole Activity can keep a checkout draft after its destination is gone. Holding a ViewBinding leaks the old view tree across rotation. Launching work in an unrelated application scope can outlive the screen and send stale updates. Conversely, assuming a ViewModel survives process death leaves a blank screen or repeats a request. Test owner removal, rotation, and process restoration separately.

## Production perspective

For search, the ViewModel owns query-to-result transformation and cancellation of obsolete requests; the repository owns caching and I/O. Scope it to the search destination so it clears when the user leaves. Save the query as a compact restoration input, reload results after a process restart, and record request IDs in diagnostics without retaining the UI or leaking user data.

## Interview answer — short

A Jetpack ViewModel is an architectural state holder that survives configuration changes by being retained within the host ViewModelStore. Its onCleared() callback is invoked exclusively when the host ViewModelStoreOwner is permanently finished—such as when an Activity finishes, a Fragment is popped from the backstack, or a Compose destination is cleared—automatically cancelling its viewModelScope.

## Interview answer — structured

A Jetpack ViewModel serves as the presentation state holder and business logic coordinator for a screen, designed specifically to decouple operational state from transient UI controllers like Activities and Fragments. It abstracts asynchronous workflows and exposes reactive state streams to the view layer.

The ViewModel survives configuration changes because it is managed by a ViewModelStore tied to a ViewModelStoreOwner. When an Activity undergoes recreation due to rotation or theme changes, the underlying Android framework transfers the existing ViewModelStore across the recreation boundary via retained non-configuration instances, ensuring that data pipelines and ongoing coroutines remain continuous.

The ViewModel must never retain a direct reference to an Activity, Fragment, View, or visual Context. Holding a UI reference inside a ViewModel pins the destroyed view hierarchy in memory across configuration changes, causing severe memory leaks.

In production, the terminal method onCleared() is executed only when the host owner is permanently destroyed, such as when an Activity calls finish() or a navigation destination is popped from the backstack. At this boundary, the runtime cancels viewModelScope and releases background sockets, caches, or event subscriptions gracefully.


## Interview answer — deep senior

At the platform architecture level, ViewModel lifecycle orchestration is governed by the ViewModelStoreOwner contract implemented by ComponentActivity, Fragment, and NavBackStackEntry. When an Activity initializes, its ViewModelProvider looks up the requested ViewModel within the Activity's ViewModelStore. If an instance already exists for that key, it is returned; otherwise, the ViewModelProvider.Factory instantiates a new one and registers it in the internal HashMap.

During an Activity configuration recreation cycle, ComponentActivity invokes onRetainNonConfigurationInstance(), encapsulating the ViewModelStore inside a platform NonConfigurationInstances object. The ActivityTaskManagerService preserves this handle in the system server's ActivityRecord. When the ActivityThread constructs the subsequent Activity instance, it supplies this cached record back via attach(). The new Activity re-adopts the same ViewModelStore, allowing ViewModelProvider to locate the exact identical ViewModel instances from heap memory without invoking their constructors or onCleared().

The invocation of onCleared() occurs strictly when the ViewModelStore.clear() method is called. ComponentActivity listens to its own Lifecycle; if the Activity transitions to DESTROYED and isFinishing() returns true, or if changingConfigurations() returns false, it concludes that the destruction is permanent. At that moment, ViewModelStore iterates over all registered ViewModel instances and triggers their clear() implementation.

Internally, ViewModel.clear() calls the protected onCleared() callback and immediately dispatches cancellation to its Closeable resources, including the internal SupervisorJob backing viewModelScope. In modern multi-module architecture, scoping ViewModels correctly to navigation graph destinations (NavBackStackEntry) or shared parent Fragment backstacks provides bounded data lifetimes, preventing stale state leakage across feature boundaries.

## How to answer in the interview

- **Why:** UI logic needs an owner that survives ordinary screen recreation.
- **How:** Define ViewModelStore scope, retention, `viewModelScope`, and clear events.
- **Trade-offs:** Keep identifiers in saved state and durable data in a repository.
- **Failure cases:** Name Activity leaks and treating process death like rotation.
- **Production solution:** Rebuild an order screen from a stable order ID after restart.

## Deep-dive talking points

Explain `ViewModelStoreOwner` identity, Activity versus destination scope, when `onCleared()` runs, how `viewModelScope` is cancelled, and why a saved key plus repository is needed for process restoration.

## Follow-up questions

- **Interviewer:** "Can a ViewModel hold a reference to an Activity or View?"
  **Answer:** "Never! Holding an Activity, View, or context reference inside a ViewModel creates a direct memory leak: when the Activity rotates and destroys its view, the ViewModel retains the dead Activity in memory, preventing garbage collection."

- **Interviewer:** "What is `AndroidViewModel` and when is it acceptable?"
  **Answer:** "`AndroidViewModel` includes a reference to `ApplicationContext`. It is acceptable if you need an Application Context for system services, but plain ViewModel with an injected context via Hilt is considered much cleaner architecture."

- **Interviewer:** "Does `onCleared()` get called during Process Death?"
  **Answer:** "No. When the OS terminates an application process via low memory kill (SIGKILL), the process dies instantly; neither onDestroy() nor onCleared() callbacks are executed."

## Self-check rubric

Name three possible owners; state what survives rotation and what does not survive process death; identify permanent clearing; choose a scope for shared versus isolated state; and explain why Activity references are dangerous.

## References and reviewed-on date

- [ViewModel overview](https://developer.android.com/topic/libraries/architecture/viewmodel) — owner scope, clearing, and screen-level logic.
- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — process restoration boundaries.

Technically reviewed against primary documentation on 2026-10-13.
