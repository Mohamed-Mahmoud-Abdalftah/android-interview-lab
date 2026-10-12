---
id: "COM-14"
question: "What are stable keys and content types in LazyColumn?"
topic: "Jetpack Compose"
code: "COM"
group: "B"
phase: 3
priority: "P1"
order: 243
editorial_status: "reviewed"
---

# COM-14

## Original interview question

What are stable keys and content types in LazyColumn?

## What the interviewer evaluates

- Distinguish item identity from item layout type.
- Explain state/scroll preservation on reorder and reuse efficiency.
- Avoid index keys for moving data and non-saveable keys where restoration matters.

## Explanation in Arabic

في `LazyColumn.items`، `key` يحدد هوية العنصر عبر insert/reorder/refresh، مثل `product.id` الفريد والثابت. بدون key مناسبة يعتمد Compose غالبًا على position، فينتقل remembered row state إلى item آخر أو يبدو scroll غير مستقر بعد تغير القائمة. `contentType` شيء مختلف: يحدد شكل/نوع المحتوى، مثل product row أو ad row، ليس ID فريد؛ يساعد إعادة استخدام composition بين عناصر من نفس النوع. keys على Android يجب تكون قابلة للحفظ في Bundle إذا احتجت حفظ state. لا تستخدم index عندما العناصر تتحرك.

## Why it matters and how it works

Lazy layouts compose visible items and reuse item compositions. Keys let the runtime associate an item's state with logical identity even when its position changes, helping scroll anchoring and item-local state. `contentType` groups structurally compatible item content for more efficient reuse. Neither fixes a data source that changes IDs unpredictably or a UI state held under a wrong list owner.

## Worked example

A feed interleaves articles and sponsored cards. Use stable article/ad IDs as keys with a type prefix if namespaces overlap, and `contentType` values such as `article` and `ad`. Refresh inserts two new articles above the viewport; with stable keys, the previously visible article remains identified. An index key would now name a different article, potentially carrying an expanded-row flag to it.

## Trade-offs and decision criteria

Stable domain IDs are ideal but sometimes backend IDs are unavailable for local drafts; create a persistent local ID rather than recomputing a hash of changing content. `contentType` helps heterogeneous lists and is less valuable when every row is identical. Verify performance in release mode; adding types does not solve expensive image decoding or large item bodies.

## Failure modes

Two items share one key and lazy state is ambiguous. A key uses mutable title text and changes after edit. Index keys cause expanded state to jump during insertion. A complex object key cannot be saved for Android state restoration. All rows are assigned the same content type despite radically different layouts.

## Production perspective

Define a stable ID contract in the data model, test insert/delete/reorder while scrolled, and assert item-local state stays with the same record. Profile heterogeneous list scrolling in a release build before tuning `contentType`.

## Interview answer — short

“`key` is stable item identity for state and position across changes; `contentType` groups similar row structures for efficient lazy composition reuse.”

## Interview answer — structured

“I key rows by a unique durable ID, not their current index, when the list can reorder or insert items. That keeps remembered row state associated with the same logical item and helps scroll continuity. `contentType` is not another key: it says whether two rows have compatible structure for reuse, such as article versus ad. I check key uniqueness and saveability on Android and test a refresh above the viewport.”

## Interview answer — deep senior

“A lazy list has two separate questions: which logical record is this, and what kind of content can its composition be reused for? A stable `key`, usually a durable domain ID, answers the first. If a feed inserts rows above the viewport, position-based identity changes and remembered expansion or input state can attach to the wrong row; stable keys allow Compose to track the same record through the move. On Android the key also needs to fit saved-state rules for restoration. I do not use a mutable title or a list index as the identity, and I distinguish ID namespaces for mixed item families. `contentType` answers the second question: an article row can be reused like another article row, while an ad card may have a different structure. It is a performance hint, not a substitute for unique identity. I test insert, delete and reorder while scrolled and with an edited row; then I profile release scrolling to see whether reuse or some other cost such as image decoding dominates. If local drafts lack server IDs, I assign stable local IDs at creation rather than deriving identity from their current content.”

## Deep-dive talking points

Cover identity versus type, position changes, Bundle-saveable keys, heterogeneous reuse, and release profiling.

## Follow-up questions

- Why is list index a poor key after insertion? **Answer:** it now identifies a different record, so item-local state can move.
- Must contentType be unique per item? **Answer:** no; compatible rows intentionally share a content type.
- What if a draft has no server ID? **Answer:** assign a stable local identifier when it is created.

## Self-check rubric

Choose keys and types for a mixed feed, predict insert behavior, and test state preservation.

## References and reviewed-on date

- [Lazy lists and grids](https://developer.android.com/develop/ui/compose/lists) — keys and content types.
- [Save UI state in Compose](https://developer.android.com/develop/ui/compose/state-saving) — restoration context.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Performance benefit must be measured for the concrete list.
