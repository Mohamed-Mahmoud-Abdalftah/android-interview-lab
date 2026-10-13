---
id: "FLO-08"
question: "What are stateIn and shareIn?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "A"
phase: 1
priority: "P1"
order: 121
editorial_status: "reviewed"
---

# FLO-08

## Original interview question

What are stateIn and shareIn?

## What the interviewer evaluates

Explain conversion of cold streams into hot shared state or broadcast, including scope and replay.

## Explanation in Arabic

`stateIn` و`shareIn` بيحوّلوا cold upstream إلى hot stream مشتركة داخل `CoroutineScope` معينة. `stateIn` يرجّع `StateFlow` بقيمة ابتدائية وآخر snapshot، مناسب UI state. `shareIn` يرجّع `SharedFlow` مع عدد replay تختاره، مناسب shared subscription. اختيار scope و`SharingStarted` يحدد عمر الاتصال وبداية/توقف الجمع؛ ما ينفعش نحط session data في scope أطول من الجلسة.

## Practical walkthrough

عندك cold Flow من Room و3 أجزاء في الشاشة عايزينها. `stateIn` تشاركها وتحتفظ بآخر قيمة مع initial state؛ `shareIn` تشارك emissions بقدر replay تختاره من غير current `.value`. الاتنين يحتاجوا scope عمرها مناسب: لو استخدمت global scope هتفضل query شغالة بعد الشاشة؛ لو scope قصيرة جدًا هتفقد sharing. اختبر وقت بدء ووقف upstream.

## Why it matters and how it works

Sharing launches an upstream collection coroutine in the supplied scope. `stateIn(scope, started, initial)` holds a current value; `shareIn(scope, started, replay)` has configurable replay. Multiple downstream collectors then share one upstream run while sharing is active. Restart and replay behavior depend on start policy and cache rules.

## Worked example

Android ViewModel example assumes DAO returns a cold `Flow<List<Item>>`; Item/Dao are app types.

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.*

class FeedViewModel(dao: FeedDao) : ViewModel() {
    val items: StateFlow<List<Item>> = dao.observeItems()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())
}
```

## Trade-offs and decision criteria

Use stateIn if callers need a current state; shareIn if replay/broadcast needs differ. Sharing saves repeated upstream work but retains data in the chosen scope and can add a buffer. `WhileSubscribed` may restart upstream; Eagerly can waste resources when nobody observes.

## Failure modes

Sharing a user-specific feed in an application scope can replay stale or sensitive data after logout. Assuming `shareIn(replay=0)` stores events for absent subscribers loses them. An initial empty list can confuse loading with empty success.

## Production perspective

A repository shares a costly location subscription in a session scope while multiple screens are active. A feed ViewModel uses stateIn for rendering. Session invalidation cancels the old scope and clears derived state.

## Interview answer — short

“`stateIn` and `shareIn` share one cold upstream in a supplied scope. `stateIn` gives current state with an initial value; `shareIn` gives configurable replay. I choose scope and start policy from the data lifetime.”

## Interview answer — structured

“A cold Flow can repeat its upstream per collector. `stateIn` launches sharing and exposes a StateFlow with a current value, which works well for ViewModel UI state. `shareIn` exposes a SharedFlow with replay I specify, useful for a shared broadcast or subscription. Both need an owner scope and a `SharingStarted` policy, because that determines when the upstream runs. I avoid an application scope for user-specific data unless session invalidation explicitly cancels and clears it.”

## Interview answer — deep senior

“I treat conversion as a resource and consistency decision. A sharing coroutine collects upstream once and fans values out, reducing duplicate database or socket subscriptions. The supplied scope sets the maximum lifetime. `stateIn` provides an initial value and latest state, with equality semantics; `shareIn` lets me choose replay count, but its buffer and no-subscriber behavior must match the consumer contract. `WhileSubscribed` can stop work offscreen and restart later, perhaps triggering a new network call. Eager sharing avoids startup delay at a resource cost. I test two simultaneous collectors, stop/restart behavior and logout so stale user state is not replayed. I would start with the consumer requirement. If callers need an immediately readable current state, `stateIn(scope, started, initialValue)` turns a cold upstream into a StateFlow. If they need a shared broadcast of emissions with configurable replay, `shareIn` returns SharedFlow. Both launch an upstream sharing coroutine in the supplied scope and need a start policy. `WhileSubscribed` can stop collection after subscribers leave, but its replay cache behavior needs separate attention; `stateIn` still exposes a value. I choose a ViewModel scope for screen state, not an unbounded global scope. I would count upstream starts with two collectors and navigate away/back to test whether the policy restarts expensive work or keeps it unnecessarily active.”

## How to answer in the interview

- **Why:** repeated cold collection can duplicate work.
- **How:** choose current state via stateIn or broadcast via shareIn.
- **Trade-off:** scope and start policy affect resources.
- **Failure case:** global sharing leaks work or wrong replay loses state.
- **Production solution:** count upstream starts through lifecycle transitions.

## Deep-dive talking points

Trace upstream subscription count, replay, start policy and scope cancellation.

## Follow-up questions

- [FLO-09](../flo-09/): Which start policy saves idle resources? **Answer:** `WhileSubscribed` can stop upstream after its timeout.
- [FLO-02](../flo-02/): Why share? **Answer:** cold collectors may duplicate expensive upstream work.

## Self-check rubric

Can I select stateIn/shareIn, name an owner, explain replay and predict restart?

## References and reviewed-on date

- [Kotlin stateIn API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/state-in.html) — state conversion.
- [Kotlin shareIn API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/share-in.html) — sharing.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
