---
id: "COM-10"
question: "What are LaunchedEffect, DisposableEffect, SideEffect, and rememberCoroutineScope?"
topic: "Jetpack Compose"
code: "COM"
group: "A"
phase: 3
priority: "P1"
order: 239
editorial_status: "reviewed"
---

# COM-10

## Original interview question

What are LaunchedEffect, DisposableEffect, SideEffect, and rememberCoroutineScope?

## What the interviewer evaluates

- Match each API to coroutine lifetime, cleanup, publication, or event-triggered launch.
- Explain key changes and composition exit.
- Avoid effects that duplicate work on recomposition.

## Explanation in Arabic

`LaunchedEffect(keys)` يطلق coroutine مرتبطة بوجود composable؛ تغيير key يلغي القديمة ويبدأ جديدة. `DisposableEffect(keys)` يسجل resource/listener ويستدعي `onDispose` عند تغيير key أو خروج composable. `SideEffect` ينفذ بعد successful recomposition لنشر state إلى object خارج Compose، وليس لتشغيل طلب طويل. `rememberCoroutineScope()` يعطي scope مرتبطة بالـcomposition لتطلق coroutine من callback مثل الضغط على زر. اختَر حسب lifetime؛ لا تضع registration في body ولا تستخدم `LaunchedEffect(Unit)` لكل user action.

## Why it matters and how it works

Compose rendering can run repeatedly. Effects provide managed points to coordinate external work with composition lifecycle. A keyed LaunchedEffect coroutine is canceled and relaunched on key change; DisposableEffect pairs setup with cleanup; SideEffect runs after a successful composition application. A remembered scope is useful for work initiated by an event handler while its call site exists.

## Worked example

A screen loads details for `userId` with `LaunchedEffect(userId)` if the work truly belongs to composition; a ViewModel may own the fetch instead. An analytics listener uses `DisposableEffect(lifecycleOwner)` to add and remove its observer. `SideEffect` publishes the latest selected category to an analytics adapter, and a button click uses a remembered scope to show a Snackbar through its host state.

## Trade-offs and decision criteria

Effect APIs make lifecycle explicit but overuse scatters business logic into UI. ViewModel-owned requests survive the composition boundary when appropriate. An event callback is preferable to a composition-triggered effect for direct user actions. Correct keys are as important as choosing the API; too broad restarts work, too narrow retains stale captures.

## Failure modes

A listener is registered on every recomposition and leaks. `LaunchedEffect(Unit)` retains an old ID. `SideEffect` performs a network request after each recomposition. A remembered scope is stored in a Singleton and launched after its composition has ended.

## Production perspective

Review every effect for its start trigger, keys, cancellation/cleanup, and owner. Test key changes, screen departure, and callback replacement. Use lifecycle-aware producers outside Compose for durable work.

## Interview answer — short

“`LaunchedEffect` runs keyed composition-owned coroutines; `DisposableEffect` pairs registration with cleanup; `SideEffect` publishes after composition; `rememberCoroutineScope` launches from callbacks.”

## Interview answer — structured

“I select by trigger and cleanup. If work should run while a keyed composable exists, I use `LaunchedEffect(key)` and accept cancel/restart when the key changes. A listener belongs in `DisposableEffect` so it is removed on key change or exit. `SideEffect` is for publishing current Compose data to non-Compose code after a successful composition. For a button-driven Snackbar I use `rememberCoroutineScope` from the event callback. Business requests often belong in ViewModel instead.”

## Interview answer — deep senior

“Effects exist because a composable body can execute again and must not casually perform external work. I ask when the work starts, what owns it, and what ends it. `LaunchedEffect` gives a coroutine whose lifetime follows the call site and its keys; a new key cancels the old job and starts a new one. `DisposableEffect` is for a paired registration and unregistration, such as a lifecycle observer, and its `onDispose` must actually release the resource. `SideEffect` runs after a successful composition to push current Compose state into an external object, so it is unsuitable for an expensive request. `rememberCoroutineScope` is useful when a click should launch a Snackbar or animation rather than when composition itself should trigger the operation. I choose keys based on the identity of the resource, and use `rememberUpdatedState` if a callback should update without restarting registration. For screen data I often prefer a ViewModel with an explicit request owner, which can survive a composable leaving temporarily. I test exit, key change and rapid callbacks because those expose stale capture and duplicate-listener bugs.”

## Deep-dive talking points

Compare keyed cancellation, disposal, post-composition publication, event scopes, and ViewModel ownership.

## Follow-up questions

- Which effect unregisters a listener? **Answer:** `DisposableEffect` with a meaningful `onDispose`.
- Should `SideEffect` call a payment API? **Answer:** no; it can run after many recompositions and has no request ownership contract.
- What happens when a `LaunchedEffect` key changes? **Answer:** its current coroutine is canceled and a new effect starts.

## Self-check rubric

Map four use cases to APIs and name keys, cleanup, and duplicate-work risks.

## References and reviewed-on date

- [Side-effects in Compose](https://developer.android.com/develop/ui/compose/side-effects) — effect contracts and keys.
- [Compose mental model](https://developer.android.com/develop/ui/compose/mental-model) — repeatable rendering.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Example ownership must match the product lifecycle.
What are LaunchedEffect, DisposableEffect, SideEffect, and rememberCoroutineScope?
