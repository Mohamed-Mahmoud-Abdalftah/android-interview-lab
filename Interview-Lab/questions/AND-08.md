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

الـViewModel بيحفظ state وlogic خاصة بـscreen عند owner معيّن: Activity أو Fragment أو navigation destination مثلًا. لما Activity تتعاد بسبب rotation، الـViewModel غالبًا بيكمل لنفس الـowner المنطقي، فتقدر تعرض الحالة بدون إعادة شغل بلا داعي. لما الـowner يختفي نهائيًا، زي `finish()` أو خروج destination من الـback stack، بيتعمل له clear و`viewModelScope` يتلغى. لو الـprocess مات، كل ViewModels تروح فورًا؛ `onCleared()` مش callback مضمون قبل قتل الـprocess. علشان كده ماتحطّش فيه Activity Context أو View، وماتعتبرهوش database.

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

“A ViewModel holds screen state and logic for a ViewModelStoreOwner. It survives ordinary configuration recreation of that owner, then is cleared when the owner is permanently removed. It does not survive process death. I keep UI references out of it and persist important data elsewhere.”

## Interview answer — structured

“The owner can be an Activity, Fragment, or navigation entry. The ViewModelStore returns the same ViewModel across recreation, which avoids unnecessary reloads and separates screen logic from views. When the owner is finished or popped, the ViewModel is cleared and its `viewModelScope` is cancelled. A killed process removes it regardless of callbacks, so I keep a saved ID for restoration and ask a repository to reload durable data. The owner determines the clearing boundary: an Activity-scoped ViewModel lasts through ordinary rotation, while a navigation-entry ViewModel clears when that entry leaves the back stack. Neither is serialized through process death. I keep view objects out of it and use a saved key plus repository reload for recovery.”
## Interview answer — deep senior

“I first choose the lifetime: destination-scoped for isolated screen state, graph- or Activity-scoped only when state genuinely spans screens. I expose immutable state, keep side effects in owned coroutines, and collect it with the UI lifecycle. The ViewModel survives configuration recreation via its store, but on permanent owner removal it is cleared and its scope is cancelled. Process death creates an entirely new graph, so I persist reconstruction keys and durable operations before they matter. I never hold an Activity or view binding in a retained ViewModel, and I test both rotation and back-stack removal. I inspect the ViewModelStoreOwner rather than say “ViewModels survive rotation” without scope. A checkout ViewModel scoped to the entire Activity may outlive its screen and hold stale draft state, while a destination-scoped instance can be cleared when navigation removes the entry. `viewModelScope` cancellation follows clearing in normal lifecycle paths; process termination is abrupt, so cleanup callbacks are not durability guarantees. A ViewModel can coordinate UI state and call a repository, but cannot be the sole payment ledger. I test owner removal, rotation and process death as distinct cases, and avoid retaining Activity or binding references across configuration changes.”
## Deep-dive talking points

Explain `ViewModelStoreOwner` identity, Activity versus destination scope, when `onCleared()` runs, how `viewModelScope` is cancelled, and why a saved key plus repository is needed for process restoration.

## Follow-up questions

- [AND-07](../and-07/): Does `onCleared()` persist state before process death? **Answer:** no; process termination need not invoke it.
- [AND-09](../and-09/): Where does a restorable order ID belong? **Answer:** small saved state; the order itself belongs in durable storage or a server.
- [MEM-09](../mem-09/): Can a ViewModel leak an Activity? **Answer:** yes, if it retains a shorter-lived Activity or view reference.

## Self-check rubric

Name three possible owners; state what survives rotation and what does not survive process death; identify permanent clearing; choose a scope for shared versus isolated state; and explain why Activity references are dangerous.

## References and reviewed-on date

- [ViewModel overview](https://developer.android.com/topic/libraries/architecture/viewmodel) — owner scope, clearing, and screen-level logic.
- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — process restoration boundaries.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The order-screen example describes architecture and was not device-tested.
