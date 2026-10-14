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

ViewModel stores and manages UI state across configuration changes, retained in memory by the ViewModelStore. Its onCleared() callback is invoked exclusively when the host lifecycle permanently finishes (e.g. Activity finishes or Fragment popped from backstack), cancelling viewModelScope automatically.

## Interview answer — structured

A Jetpack ViewModel is designed to hold and manage UI-related state in a lifecycle-conscious way, surviving configuration changes and decoupling business logic from UI controllers.

It survives configuration changes because it is retained by a `ViewModelStore`. During rotation, Android passes the `ViewModelStore` from the destroyed Activity to the newly created Activity via `onRetainNonConfigurationInstance()`.

**When it is cleared (`onCleared()`):**
`onCleared()` is invoked when the associated `ViewModelStoreOwner` is permanently finished and destroyed.

First, when an Activity finishes intentionally (user taps Back or `finish()` is called, where `isFinishing == true`). Next, when a Fragment is permanently removed or popped from the backstack.
Finally, when a Jetpack Compose navigation route (`NavBackStackEntry`) is popped from the backstack.

When cleared, the framework automatically cancels the built-in `viewModelScope`, cleaning up all active coroutines.


## Interview answer — deep senior

Under the hood, `ViewModelProvider` retrieves existing ViewModels from `ViewModelStore` using a String key (e.g., `androidx.lifecycle.ViewModelProvider.DefaultKey:MyViewModel`). If an instance exists, it returns the existing object without invoking the constructor. If not, it uses the `ViewModelProvider.Factory` to instantiate it.

In modern multi-fragment or Compose architectures, you can scope ViewModels to different owners: - **Activity-scoped (`activityViewModels()`):** Shares state across sibling fragments or tabs. - **Navigation Graph-scoped (`navGraphViewModels(R.id.checkout_graph)`):** Scopes the ViewModel to a specific multi-step user flow (like Checkout). When the flow finishes, the ViewModel clears automatically, releasing memory. - **Fragment/Destination-scoped:** Clears when that specific screen terminates.


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
