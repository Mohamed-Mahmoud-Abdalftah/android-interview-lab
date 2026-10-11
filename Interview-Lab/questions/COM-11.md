---
id: "COM-11"
question: "Compare LaunchedEffect(Unit) and LaunchedEffect(key)."
topic: "Jetpack Compose"
code: "COM"
group: "B"
phase: 3
priority: "P1"
order: 240
editorial_status: "reviewed"
---

# COM-11

## Original interview question

Compare LaunchedEffect(Unit) and LaunchedEffect(key).

## What the interviewer evaluates

- Explain effect lifetime at one call site versus restart on changing identity.
- Identify stale capture and unnecessary restarts.
- Choose ViewModel ownership when work should outlive composition.

## Explanation in Arabic

`LaunchedEffect(Unit)` key ثابت: effect يبدأ عند دخول call site للـcomposition، لا يبدأ لمجرد recomposition عادية، لكنه يتوقف عندما يخرج ويرجع يبدأ إذا دخل من جديد. `LaunchedEffect(userId)` يتوقف ويبدأ عند تغير `userId`، فيمنع طلب بيانات ID قديم من الاستمرار كأنه الحالي. استخدام Unit مع قيمة متغيرة داخل block قد يقرأ قيمة قديمة؛ إما اجعل القيمة key إذا تغيرها يغير هوية العمل، أو `rememberUpdatedState` إذا تريد أحدث callback دون restart. لا تعتمد على effect composable لعمل لازم يكمل بعد مغادرة الشاشة.

## Why it matters and how it works

LaunchedEffect ties a coroutine to composition and its key set. A stable key avoids restart during ordinary recomposition at the same call site. A changed key cancels the old coroutine and starts the block again. The key should represent the identity that requires a new operation; unrelated state in the key causes needless cancellation, while missing identity causes stale work.

## Worked example

`LaunchedEffect(articleId)` scrolls to or loads information for the current article. Navigating from article A to B without leaving the same composable call site cancels A's composition-owned operation and starts B's. A one-time entrance animation with no input identity can use `Unit`. If the repository load belongs to a ViewModel and must survive temporary UI absence, invoke it from that owner instead.

## Trade-offs and decision criteria

Constant keys are simple for call-site lifetime tasks, but can conceal stale inputs. Variable keys handle identity changes but restart expensive work when keys change frequently. A ViewModel operation follows its own lifecycle and can better coordinate deduplication, caching or navigation.

## Failure modes

A user ID changes while a Unit-keyed effect continues listening to the old account. A lambda passed as key changes every recomposition and restarts the effect repeatedly. A long payment submission is canceled when the composable exits, leaving unknown status without a durable recovery path.

## Production perspective

Document each effect's identity and cancellation semantics. Test navigation between IDs without recreating the whole Activity, and observe side-effect starts under recomposition. For durable or high-value requests, use a stable owner and backend recovery.

## Interview answer — short

“`LaunchedEffect(Unit)` runs for one composition call-site lifetime; `LaunchedEffect(key)` cancels and restarts when that key changes.”

## Interview answer — structured

“Unit is appropriate when entering the composition is the trigger and no changing input defines the work. A meaningful key, such as `articleId`, makes the effect restart when the resource identity changes. Neither restarts on every ordinary recomposition with the same key. I avoid stale captures with the right key or `rememberUpdatedState`, and I avoid using a composition-owned effect for work that must survive leaving the screen.”

## Interview answer — deep senior

“I interpret the key as the identity of the side effect. With `LaunchedEffect(Unit)`, the block begins when that call site enters composition and is canceled when it leaves; recomposition at the same site does not restart it. That works for an entrance animation or a listener whose owner truly is the current call site, provided changing callbacks are handled correctly. With `LaunchedEffect(articleId)`, changing the article cancels the previous coroutine and starts a new one for the new ID. That is useful when old work must stop, but it can be destructive if the key is an unstable object or a rapidly changing text field. I audit which values the block captures: values that define work identity belong in the keys; callbacks that should be current without resetting registration may use `rememberUpdatedState`. I also check the scope boundary. A payment submission or repository sync that must outlive a temporary composition exit should be owned by a ViewModel or durable worker with recovery semantics, not hidden behind a Unit-keyed effect. Tests should change the key, recompose with the same key, and remove the composable to verify exactly which operations are canceled or repeated.”

## Deep-dive talking points

Explain call-site identity, cancellation, key selection, stale captures, and durable ownership.

## Follow-up questions

- Does Unit restart on every recomposition? **Answer:** no; only a new entrance at that call site starts it again.
- Why not use an unstable lambda as a key? **Answer:** identity changes can trigger unintended cancellation and restart.
- When would `rememberUpdatedState` help? **Answer:** when an effect should retain its registration but call the latest provided callback.

## Self-check rubric

Choose keys for two examples, explain cancellation, and identify one task that belongs outside composition.

## References and reviewed-on date

- [Side-effects in Compose](https://developer.android.com/develop/ui/compose/side-effects) — key and cancellation behavior.

Technically reviewed against this primary source on 2026-10-11 by automated editorial review. Durable payment ownership is an engineering recommendation.
Compare LaunchedEffect(Unit) and LaunchedEffect(key).
