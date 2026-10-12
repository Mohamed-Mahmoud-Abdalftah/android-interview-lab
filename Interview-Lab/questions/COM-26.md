---
id: "COM-26"
question: "A LazyColumn scroll position resets after data refresh. What should you inspect?"
topic: "Jetpack Compose"
code: "COM"
group: "C"
phase: 3
priority: "P1"
order: 255
editorial_status: "reviewed"
---

# COM-26

## Original interview question

A LazyColumn scroll position resets after data refresh. What should you inspect?

## What the interviewer evaluates

- Inspect LazyListState ownership and composable identity.
- Distinguish item keys and data reorder from an actual state reset.
- Define desired scroll policy for refresh/new query and restoration.

## Explanation in Arabic

أولًا اسأل: هل المطلوب البقاء عند نفس item أم العودة للأول بعد query جديدة؟ افحص `rememberLazyListState()` هل موجود في call site ثابت أم Screen تُزال/تتغير key فيُنشأ state جديد. ثم keys للعناصر: IDs ثابتة وفريدة تساعد Compose يتتبع item بعد insertion/reorder؛ index keys تجعل الصفوف تتبدل هويتها. راجع هل refresh تستبدل list بنفس IDs أم تولد IDs جديدة، وهل code يستدعي `scrollToItem(0)` في effect بكل emission. `LazyListState` له saveable behavior، لكن restoration تعتمد على owner وبقاء saved state.

## Why it matters and how it works

Scroll state tracks index and offset, and lazy item keys can help maintain logical position when data changes. A `rememberLazyListState` bound to a removed composition location is recreated. An effect that scrolls on every dataset update overrides remembered position. If a refreshed data set has different identity or sort order, preserving the same index may be semantically wrong even when technically possible.

## Worked example

A feed inserts three newer posts above a user reading post ID 42. Stable post IDs allow the reader to remain anchored near post 42; a root `key(refreshToken)` recreates the entire list state and jumps to top. Remove that root key, keep one list state for the destination, and scope a top-scroll effect only to an explicit new search filter, not every refresh emission.

## Trade-offs and decision criteria

Maintaining position is good for incremental refresh but may confuse users when a new query replaces the dataset. A deliberate top reset on filter change should be explicit. Holding list state too high can carry an old feed's offset into a different account. Stable keys incur little complexity when domain IDs exist.

## Failure modes

Index keys cause row-local state to jump. `rememberLazyListState()` is inside a condition that disappears during Loading. A LaunchedEffect keyed by the whole list calls `animateScrollToItem(0)` after every refresh. Backend IDs change across responses, defeating item identity. Saveability is assumed even though the destination is fully removed from back stack.

## Production perspective

Test refresh insertions above viewport, deletion of current item, query/account switch, navigation return and process recreation. Record first visible ID and offset before/after to distinguish item anchoring from index behavior.

## Interview answer — short

“I inspect list-state ownership, stable item IDs, any scroll effect triggered by refresh, and the product's desired policy for data changes.”

## Interview answer — structured

“First I ask whether refresh should retain the same item or reset for a new query. I check that `LazyListState` is remembered at a stable call site and not recreated by a loading branch or root key. Then I verify unique stable item keys and whether the backend preserves IDs. Finally I look for `scrollToItem(0)` effects keyed to every list emission. I test inserts above the viewport and account/filter changes separately.”

## Interview answer — deep senior

“A jump to top can come from three different causes, so I instrument the first visible item ID, index and offset before and after refresh. One cause is owner recreation: the list may leave composition during Loading or sit under a changing `key(refreshToken)`, so `rememberLazyListState()` is new. Another is item identity: if rows use positions as keys, inserting records above the viewport changes which item an index refers to and can move remembered row state. The third is explicit code, such as a `LaunchedEffect(items)` that scrolls to zero after every emission. I fix the actual cause rather than forcing an offset restore blindly. Stable IDs and a persistent destination-owned list state fit incremental updates, while a genuinely new search query may intentionally reset to top. I keep account and filter identity in that policy so an old feed offset does not leak into another dataset. I test insert, delete, reorder, navigation return and eligible process recreation, including the case where the formerly visible item is removed.”

## Deep-dive talking points

Cover LazyListState ownership, item keys, refresh semantics, explicit scroll commands, and restoration tests.

## Follow-up questions

- Can stable item keys repair a newly created LazyListState? **Answer:** no; owner recreation is a separate problem.
- Should every refresh preserve exact index? **Answer:** no; preserve logical item or reset based on product semantics.
- Why inspect `LaunchedEffect(items)`? **Answer:** it may execute a scroll command for every data emission.

## Self-check rubric

Distinguish three causes, propose one measurement, and define refresh versus new-query behavior.

## References and reviewed-on date

- [Lazy lists and grids](https://developer.android.com/develop/ui/compose/lists) — keys and list state.
- [Save UI state in Compose](https://developer.android.com/develop/ui/compose/state-saving) — saveable state.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Exact scroll policy is a product decision.
