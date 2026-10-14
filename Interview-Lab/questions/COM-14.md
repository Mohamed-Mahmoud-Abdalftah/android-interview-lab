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

أهمية المفاتيح المستقرة (`keys`) وأنواع المحتوى (`contentType`) في قوائم `LazyColumn` و `LazyRow`:

1. المشكلة عند عدم استخدام `key` في `LazyColumn`:
   - افتراضياً، إذا لم تحدد `key`، يستخدم Compose **موضع العنصر (Item Position/Index)** كمفتاح افتراضي.
   - إذا أضفت عنصراً في بداية القائمة أو قمت بترتيب العناصر:
     * يتغير موضع كل العناصر التالية (العنصر 0 أصبح 1، و 1 أصبح 2).
     * يعتقد Compose أن كل عنصر قد تغير بالكامل، فيقوم بـ **إعادة تركيب (Recomposition) وإعادة تهيئة كل العناصر**!
     * تفقد العناصر حالتها الداخلية (مثل حالة التمرير، أو النص المكتوب داخل العنصر، أو الرسوم المتحركة).

2. دور المفاتيح المستقرة (`key = { item.id }`):
   - يمنح كل عنصر هوية فريدة وثابتة (Semantic Identity).
   - عندما تتغير القائمة، يستطيع Compose معرفة أي عنصر تحرك بدقة، فيقوم بنقله بسلاسة وتخطي إعادة تركيبه بالكامل (`Smart Skipping`).
   - يدعم خاصية الرسوم المتحركة التلقائية لحركة العناصر عبر `Modifier.animateItemPlacement()`.

3. دور نوع المحتوى (`contentType`):
   - في القوائم غير المتجانسة (Heterogeneous Lists التي تحتوي على رؤوس أقسام Headers، بطاقات إعلانات Ads، وبطاقات عادية Cards):
   - يخبر `contentType` محرك Compose بنوع الـ Layout حتى يقوم **بإعادة تدوير الـ Composition Slots (Composition Recycling)** بين العناصر المتشابهة في التركيب بدلاً من التدمير وإعادة البناء من الصفر.

## Practical walkthrough

الاستخدام الاحترافي لـ key و contentType في LazyColumn:
```kotlin
sealed interface FeedItem {
    val id: String
    data class Header(override val id: String, val title: String) : FeedItem
    data class Post(override val id: String, val text: String, val author: String) : FeedItem
    data class Ad(override val id: String, val bannerUrl: String) : FeedItem
}

@Composable
fun FeedList(items: ImmutableList<FeedItem>, modifier: Modifier = Modifier) {
    LazyColumn(modifier = modifier) {
        items(
            items = items,
            key = { item -> item.id }, // مفتاح مستقر فريد يحمي الحالة ويسرع السكرول
            contentType = { item ->
                // تصنيف نوع المحتوى لإعادة تدوير الـ Slots بين العناصر المتشابهة:
                when (item) {
                    is FeedItem.Header -> "HEADER_TYPE"
                    is FeedItem.Post -> "POST_TYPE"
                    is FeedItem.Ad -> "AD_TYPE"
                }
            }
        ) { item ->
            when (item) {
                is FeedItem.Header -> HeaderView(item)
                is FeedItem.Post -> PostCard(item)
                is FeedItem.Ad -> AdBanner(item)
            }
        }
    }
}
```

## Why it matters and how it works

Lazy layouts compose visible items and reuse item compositions. Keys let the runtime associate an item's state with logical identity even when its position changes, helping scroll anchoring and item-local state. `contentType` groups structurally compatible item content for more efficient reuse. Neither fixes a data source that changes IDs unpredictably or a UI state held under a wrong list owner.

## Worked example

A feed interleaves articles and sponsored cards. Use stable article/ad IDs as keys with a type prefix if namespaces overlap, and `contentType` values such as `article` and `ad`. Refresh inserts two new articles above the viewport; with stable keys, the previously visible article remains identified. An index key would now name a different article, potentially carrying an expanded-row flag to it.

### Compose/Kotlin walkthrough

```kotlin
// FeedItem has stable id and distinct Article/Ad variants.
LazyColumn(state = rememberLazyListState()) {
    items(
        items = feed,
        key = { item -> "${item.type}:${item.id}" },
        contentType = { item -> item.type }
    ) { item ->
        FeedRow(item)
    }
}
// Imports: androidx.compose.foundation.lazy.LazyColumn/items/rememberLazyListState.
```

## Trade-offs and decision criteria

Stable domain IDs are ideal but sometimes backend IDs are unavailable for local drafts; create a persistent local ID rather than recomputing a hash of changing content. `contentType` helps heterogeneous lists and is less valuable when every row is identical. Verify performance in release mode; adding types does not solve expensive image decoding or large item bodies.

## Failure modes

Two items share one key and lazy state is ambiguous. A key uses mutable title text and changes after edit. Index keys cause expanded state to jump during insertion. A complex object key cannot be saved for Android state restoration. All rows are assigned the same content type despite radically different layouts.

## Production perspective

Define a stable ID contract in the data model, test insert/delete/reorder while scrolled, and assert item-local state stays with the same record. Profile heterogeneous list scrolling in a release build before tuning `contentType`.

## Interview answer — short

In `LazyColumn`, specifying a unique `key` anchors each item to its data ID rather than its index position, preserving item state across insertions/deletions and enabling item placement animations. Providing `contentType` allows Compose to recycle slot table compositions between items with matching layouts, reducing composition overhead.

## Interview answer — structured

In `LazyColumn` and `LazyRow`, configuring `key` and `contentType` is vital for fluid 120fps scrolling and correct state preservation.

First, with Stable Keys (`key`), by default, Compose uses item index as the implicit key. If an item is prepended at index 0, every existing item shifts down, causing Compose to believe all items mutated and forcing a recomposition of the entire visible viewport. Furthermore, item-level state (like text field inputs or expanded accordions) shifts onto the wrong items! Providing a persistent, unique identifier (`key = { it.id }`) preserves item identity, retains local state correctly across reorderings, and powers smooth animations via `Modifier.animateItem()`. Finally, with Content Types (`contentType`), in heterogeneous lists featuring multiple visual layouts (e.g. Header, Card, VideoPlayer, AdBanner), Compose uses `contentType` to group structurally similar items. This enables Compose to recycle Slot Table structures exclusively among items of the same type, drastically cutting down allocation overhead and layout measurement passes during rapid fling scrolls.


## Interview answer — deep senior

Under the hood, keys in `LazyLayout` must be parcelable or persistable in Android bundles because Compose uses them to retain `rememberSaveable` state per item in the `LazyLayoutItemContentFactory`. If an invalid non-unique key is used, Compose throws an `IllegalArgumentException` indicating duplicate keys within the composition.

Without `contentType`, when a user scrolls and an AdBanner leaves the screen while a simple PostCard enters, Compose attempts to reuse the slot composition of the AdBanner for the PostCard. Because the composable structures mismatch completely, Compose must discard the slot group and execute a full new composition from scratch. With `contentType`, Compose preserves separate recycling pools for each layout signature, matching the recycling efficiency of `RecyclerView.getItemViewType()`.

In Macrobenchmark scroll tests, adding both `key` and `contentType` to complex feeds typically slashes frame drop rates during rapid scrolls by 40-60%.


## How to answer in the interview

- **Why:** lazy rows need durable identity across insertion and reorder.
- **How:** distinguish unique key from reusable content type.
- **Trade-off:** key values must stay stable and be saveable for item state restoration.
- **Failure case:** index or regenerated IDs move local state.
- **Production solution:** test refresh while scrolled and expanded.

## Deep-dive talking points

Cover identity versus type, position changes, Bundle-saveable keys, heterogeneous reuse, and release profiling.

## Follow-up questions

- **Interviewer:** "What happens if two items in a LazyColumn produce the same key?"
  **Answer:** "Compose crashes immediately at runtime with an `IllegalArgumentException: Key '...' was already used. If you are using LazyColumn, you must ensure that all keys are unique."

- **Interviewer:** "Can you use item index as a key in `LazyColumn`?"
  **Answer:** "Specifying index explicitly is redundant because it is already the default behavior. It fails to preserve state during insertions, deletions, and sorting, and should be avoided in dynamic lists."

## Self-check rubric

Choose keys and types for a mixed feed, predict insert behavior, and test state preservation.

## References and reviewed-on date

- [Lazy lists and grids](https://developer.android.com/develop/ui/compose/lists) — keys and content types.
- [Save UI state in Compose](https://developer.android.com/develop/ui/compose/state-saving) — restoration context.

Technically reviewed against primary documentation on 2026-10-13.
