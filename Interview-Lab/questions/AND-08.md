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

A Jetpack ViewModel holds and coordinates screen-level UI state for a particular `ViewModelStoreOwner`, such as an Activity, Fragment, or navigation back-stack entry. Looking it up again from the same store returns the same instance. The store is retained across eligible configuration recreation, so the new UI object can reuse its ViewModel; this *can* avoid repeated work when the state and repository are designed for it, but does not eliminate every network request or database query.

The owner determines clearing. When that owner is removed for good—for example, an Activity finishes or a destination is popped—its store is cleared and the ViewModel receives `onCleared()`. `viewModelScope` is cancelled when the ViewModel is cleared. Current AndroidX ViewModel also closes registered resources *before* calling `onCleared()`, so do not assert that `onCleared()` always runs first. A ViewModel does not survive process death as the same object, and process termination need not invoke `onCleared()`. Keep small restoration inputs in saved state and durable data in a repository or database. Avoid retaining an Activity, Fragment, or View in a longer-lived ViewModel.

## Practical walkthrough (English)

For a chat destination, choose the navigation entry as owner if the socket is only useful while that destination remains. This AndroidX sketch assumes app-owned `ChatSocketManager` and `MessageRepository` implementations:
```kotlin
class ChatViewModel(
    private val chatSocket: ChatSocketManager,
    private val repository: MessageRepository
) : ViewModel() {

    init {
        // App-owned socket may need connection/reconnection policy beyond this screen.
        chatSocket.connect()
    }

    fun sendMessage(text: String) {
        viewModelScope.launch {
            repository.dispatchMessage(text)
        }
    }

    override fun onCleared() {
        super.onCleared()
        // Cleanup when this owner clears the ViewModel; not a process-death callback.
        chatSocket.disconnect()
    }
}
```
On eligible rotation, the owner retains the store, but the socket itself can still disconnect for network reasons. An image preview may or may not share this ViewModel; that depends on which navigation entry owns it. When the chat entry is popped, its store is cleared and the socket cleanup runs. If Android kills the whole process, no cleanup callback is guaranteed. On restoration, create a new ViewModel and reconnect from a stable chat ID, rather than treating the old socket or in-memory message list as durable.

## Explanation in Arabic

الـ`ViewModel` مكان يحتفظ بحالة الشاشة وينسّق شغلها، لكن عمره بيتحدد بالـ`ViewModelStoreOwner` اللي طلبته منه: Activity أو Fragment أو Nav Back Stack Entry. لو حصل Configuration Change مؤهل، الـUI القديمة تتبني من جديد والـOwner يحتفظ بالـStore، فتقدر النسخة الجديدة تستخدم نفس ViewModel. ده ممكن يوفر إعادة تحميل لو أنت مصمم الـState والـRepository بالشكل المناسب؛ مش ضمان إن مفيش Network Request تاني.

لما الـOwner يتشال نهائيًا، زي Pop لوجهة التنقل، الـStore يتصفّر والـViewModel تتعملها Clear. `viewModelScope` بتتلغى، و`onCleared()` مكان مناسب لتنظيف مورد مربوط بعمرها. في AndroidX الحديثة، الـCloseables المسجلة بتتقفل قبل `onCleared()`؛ متفترضش ترتيب عكسي. لو الـProcess اتقتل، الـCallback مش مضمونة أصلًا، والـViewModel القديمة مش هترجع. احفظ `chatId` صغير في Saved State واسترجع الرسائل من Repository أو مصدر دائم. ما تخزنش Activity أو View جوّه ViewModel أطول عمرًا منها.

## Practical walkthrough

في شاشة محادثة، خليك واضح مين مالك الـViewModel: لو هي تخص وجهة واحدة، استخدم الـNav Entry بدل Activity كلها. الكود ده توضيحي ويحتاج أنواع التطبيق واعتماديات AndroidX:
```kotlin
class ChatViewModel(private val chatSocket: ChatSocket) : ViewModel() {
    init {
        // الاتصال قد ينقطع لأسباب شبكة حتى مع بقاء الـ ViewModel.
        chatSocket.connect()
    }

    override fun onCleared() {
        super.onCleared()
        // تنظيف مورد تابع لعمر الـ Owner؛ ليست Callback لموت الـ Process.
        chatSocket.disconnect()
    }
}
```
عند Rotation مؤهل غالبًا نفس ViewModel تفضل، لكن الـSocket نفسها ممكن تفصل. لما تخرج الـChat Entry من الـBack Stack، الـOwner يمسح الـStore. لو النظام قتل الـProcess، اعمل ViewModel جديدة وحمّل المحادثة من `chatId`؛ لا تنتظر `onCleared()` كإشارة حفظ.

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

A ViewModel is a screen-state holder scoped to a `ViewModelStoreOwner`. Its instance can survive eligible configuration recreation because the owner retains its store. When that owner is finally removed, the ViewModel is cleared and `viewModelScope` is cancelled. Process death destroys the instance without a guaranteed `onCleared()` callback, so important data needs a separate restoration source.

## Interview answer — structured

A ViewModel keeps state and coordinates screen work for one `ViewModelStoreOwner`. I choose the owner first: Activity for genuinely shared state, Fragment or navigation entry for a specific screen. During eligible configuration recreation, that store can be retained and the new UI controller requests the same ViewModel instance. The instance may retain a chat's current UI state, but the network socket can still fail independently. When the owner is removed for good, the store clears the ViewModel, cancelling `viewModelScope` and invoking cleanup. For example, popping a chat destination should release a chat-only socket or subscription. I keep a stable chat ID in saved state and messages in the repository so a new ViewModel can rebuild after process death. I avoid holding Activity, Fragment, or View references in the ViewModel because their lifetime may be shorter. A plain local state holder can be enough for small visual state; ViewModel is useful when screen-level state and work need this owner boundary.


## Interview answer — deep senior

`ViewModelProvider` resolves a key in its owner's `ViewModelStore`, creating an instance with a factory only if that key is absent. The relevant public contract is ownership and retention, not an assumption about a particular `ActivityThread` or system-server implementation. An Activity, Fragment, or navigation entry can own a store; choosing a wider owner intentionally shares the ViewModel but also keeps its state around longer. Configuration recreation may reattach the retained store, while popping a navigation entry clears its store. A ViewModel scoped to the Activity is not necessarily cleared when just one child screen is popped.

The clearing contract has details that matter for cleanup. AndroidX ViewModel closes registered keyed, constructor, and unkeyed `AutoCloseable` resources before it invokes `onCleared()`. The associated `viewModelScope` is cancelled as part of clearing, so child coroutines do not run indefinitely after that boundary. This cancellation is cooperative; an uncooperative blocking call may not stop instantly. You can use `onCleared()` for a socket or listener that is truly owned by this ViewModel, or register a closeable with the ViewModel. Neither approach is a durable finalization callback: an OS process kill can happen without invoking it.

For a chat screen, an Activity-scoped ViewModel may unnecessarily keep the chat session when navigation moves elsewhere; a destination-scoped one can have a tighter lifetime. But using a screen-scoped socket also means it must reconnect if the user returns after popping the entry. Connection continuity is a network/product decision, not guaranteed by ViewModel retention. After process death, a new ViewModel uses a saved conversation ID to load messages from a durable source; a payment or message send must not rely on `onCleared()` to commit. I would test rotation, destination pop, process recreation, and network disconnect separately.

## How to answer in the interview

- **Why:** UI logic needs an owner that survives ordinary screen recreation.
- **How:** Define ViewModelStore scope, retention, `viewModelScope`, and clear events.
- **Trade-offs:** Keep identifiers in saved state and durable data in a repository.
- **Failure cases:** Name Activity leaks and treating process death like rotation.
- **Production solution:** Rebuild an order screen from a stable order ID after restart.

## Deep-dive talking points

Explain `ViewModelStoreOwner` identity, Activity versus destination scope, when `onCleared()` runs, how `viewModelScope` is cancelled, and why a saved key plus repository is needed for process restoration.

## Follow-up questions

- **Interviewer:** "Why avoid holding an Activity or View in a ViewModel?"
  **Answer:** "The ViewModel may outlive that UI instance across configuration recreation. A strong reference can retain a destroyed view tree or Activity. Keep UI references with the UI owner and inject a repository for longer-lived work."

- **Interviewer:** "Would you put a WebSocket inside a chat ViewModel?"
  **Answer:** "Only if its lifetime really matches that owner's lifetime. A shared chat connection may belong in a repository; a screen-only subscription can be closed when its ViewModel clears. Either way, I handle network drops and process recreation."

- **Interviewer:** "Does `onCleared()` get called during Process Death?"
  **Answer:** "No. When the OS terminates an application process via low memory kill (SIGKILL), the process dies instantly; neither onDestroy() nor onCleared() callbacks are executed."

## Self-check rubric

Name three possible owners; state what survives rotation and what does not survive process death; identify permanent clearing; choose a scope for shared versus isolated state; and explain why Activity references are dangerous.

## References and reviewed-on date

- [ViewModel overview](https://developer.android.com/topic/libraries/architecture/viewmodel) — owner scope, clearing, and screen-level logic.
- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — process restoration boundaries.
- [ViewModel API](https://developer.android.com/reference/androidx/lifecycle/ViewModel) — resource close order and `viewModelScope` cancellation.

Technically reviewed against primary documentation on 2026-10-19. Chat code is illustrative AndroidX code, not compiled in this repository.
