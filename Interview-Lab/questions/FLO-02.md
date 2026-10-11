---
id: "FLO-02"
question: "Explain cold flows and what happens with multiple collectors."
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "A"
phase: 1
priority: "P1"
order: 115
editorial_status: "reviewed"
---

# FLO-02

## Original interview question

Explain cold flows and what happens with multiple collectors.

## What the interviewer evaluates

Predict repeated execution for two cold-flow collectors and choose sharing deliberately.

## Explanation in Arabic

الـcold Flow مش بتبدأ upstream غير وقت collection. لو اتنين عملوا `collect` لنفس `flow {}`، block هيتنفذ مرتين، فلو فيه HTTP call ممكن تبقى طلبين. ده مفيد لو كل collector عايز execution مستقلة، لكنه مكلف لو المصدر واحد؛ ساعتها نشارك بـ`shareIn` أو `stateIn` داخل scope مملوكة.

## Why it matters and how it works

Intermediate operators stay lazy. Each collection gets a separate flow execution unless the source itself is hot or has external cache. `shareIn` starts one sharing coroutine in a supplied scope; `stateIn` additionally keeps one latest value. Start policies determine when that upstream starts/stops.

## Worked example

JVM example uses `kotlinx-coroutines-core`; `calls` increments once per collection, illustrating duplicate upstream execution.

```kotlin
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.toList

suspend fun demo(): Int {
    var calls = 0
    val cold = flow { calls++; emit(calls) }
    cold.toList()
    cold.toList()
    return calls // 2
}
```

## Trade-offs and decision criteria

Sharing saves duplicate subscriptions but introduces scope lifetime, replay and freshness decisions. Do not share a user-specific stream in an application scope without session invalidation. A cached repository source may already prevent duplicated HTTP even if its Flow is cold; inspect the implementation.

## Failure modes

Two composables independently collecting a cold refresh Flow can cause duplicate API calls. A shared stream can also outlive logout and replay another user’s state if scoped incorrectly. Choose the owner and reset policy explicitly.

## Production perspective

A Room DAO Flow may run separate observations for two collectors; a ViewModel uses `stateIn(viewModelScope, WhileSubscribed(...), initial)` to expose a single UI state. A session switch destroys or replaces the ViewModel state and invalidates cache.

## Interview answer — short

“Cold means upstream runs for each collector. Two collections of a `flow { fetch() }` can call `fetch` twice. If I need one shared source, I convert it with `shareIn` or `stateIn` in an owned scope and choose replay/start behavior.”

## Interview answer — structured

“I expect a cold Flow to be lazy and repeatable. Building the pipeline does not fetch data; each terminal collection runs it. That is a good contract for independent requests, but two UI collectors can duplicate an expensive subscription or network call. I use `stateIn` for a latest-value UI state or `shareIn` for a shared event-like stream, with a ViewModel or session scope and an explicit `SharingStarted` policy. I verify whether the repository already caches, because coldness at the Flow layer does not tell the whole network story. Sharing saves duplicate subscriptions but introduces scope lifetime, replay and freshness decisions. Do not share a user-specific stream in an application scope without session invalidation. A cached repository source may already prevent duplicated HTTP even if its Flow is cold; inspect the implementation.”

## Interview answer — deep senior

“I would trace where side effects occur. `flow { api.load(); emit(...) }` executes that API call per collector. A `map` chain does not change that; only a terminal operation starts it. Sharing inserts one coroutine that collects upstream and broadcasts values, but now correctness depends on owner lifetime, replay count and start/stop timing. A `WhileSubscribed` policy can save work when no UI is active but may restart the source on rotation. For session data I avoid application-wide replay that could expose stale account state after logout. Tests count upstream subscriptions under two collectors and after stop/start, rather than inferring sharing from type names. Each collection gets a separate flow execution unless the source itself is hot or has external cache. `shareIn` starts one sharing coroutine in a supplied scope; `stateIn` additionally keeps one latest value. Start policies determine when that upstream starts/stops. Two composables independently collecting a cold refresh Flow can cause duplicate API calls. A shared stream can also outlive logout and replay another user’s state if scoped incorrectly. Choose the owner and reset policy explicitly. A Room DAO Flow may run separate observations for two collectors; a ViewModel uses `stateIn(viewModelScope, WhileSubscribed(...), initial)` to expose a single UI state. A session switch destroys or replaces the ViewModel state and invalidates cache.”

## Deep-dive talking points

Compare per-collector side effects, external caches, sharing scope and stale replay on session change.

## Follow-up questions

- [FLO-08](../flo-08/): What creates a hot shared stream? **Answer:** `shareIn` or `stateIn` launches sharing in a supplied scope.
- [FLO-09](../flo-09/): When might upstream restart? **Answer:** with `WhileSubscribed` after subscriptions stop and later resume.

## Self-check rubric

Can I predict subscription count, choose sharing, and identify its scope and replay risk?

## References and reviewed-on date

- [Kotlin Flow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/) — cold collection.
- [Kotlin shareIn API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/share-in.html) — shared upstream.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
