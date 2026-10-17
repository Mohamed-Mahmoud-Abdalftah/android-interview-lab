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

## Concept and technical explanation

In Jetpack Compose Lazy layouts, stable keys and content types are vital optimization mechanisms that govern item identity and composition recycling. A stable key (provided via key = { item.id }) supplies a unique, persistent identifier for each item instead of relying on default list position indices, preserving scroll position and enabling item placement animations during dataset mutations. The contentType parameter (provided via contentType = { item.type }) classifies items by their visual layout structure, allowing the Compose subcomposition pipeline to reuse composition slots and SlotTable layouts between items of identical structure, mirroring legacy RecyclerView view pools.

## Practical walkthrough (English)

Applying stable keys and content types in a heterogeneous LazyColumn:
```kotlin
sealed interface FeedItem {
    val id: String
    data class Header(override val id: String, val title: String) : FeedItem
    data class Post(override val id: String, val content: String, val author: String) : FeedItem
    data class BannerAd(override val id: String, val adUrl: String) : FeedItem
}

@Composable
fun FeedList(items: List<FeedItem>, modifier: Modifier = Modifier) {
    LazyColumn(modifier = modifier) {
        items(
            items = items,
            // 1. STABLE KEY: Preserves scroll state, avoids item recreation on insert/delete
            key = { item -> item.id },
            // 2. CONTENT TYPE: Reuses composition slots between identical layout structures!
            contentType = { item ->
                when (item) {
                    is FeedItem.Header -> "HEADER_TYPE"
                    is FeedItem.Post -> "POST_TYPE"
                    is FeedItem.BannerAd -> "AD_TYPE"
                }
            }
        ) { item ->
            when (item) {
                is FeedItem.Header -> HeaderItemView(item)
                is FeedItem.Post -> PostItemView(item)
                is FeedItem.BannerAd -> AdBannerView(item)
            }
        }
    }
}
```

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

Stable keys and content types optimize LazyColumn performance. A stable key provides a unique, persistent identity (like an ID) for each item, preventing scroll jumps, avoiding state loss, and enabling item placement animations when the list changes. The contentType classifies items by their visual structure, allowing Compose to reuse composition slots and nodes between items of the same type, drastically reducing allocation and measurement overhead during fast scrolling.

## Interview answer — structured

Achieving smooth 60fps scrolling in Jetpack Compose Lazy lists relies directly on configuring stable keys and explicit content types.
By default, if you omit the key parameter in items(), LazyColumn uses the item's integer position in the list as its identity.
This default behavior causes severe bugs when the list updates dynamically.
If an item is prepended at index zero, every existing item's index shifts by one. Compose assumes every item has been replaced, discarding item-level remembered state, losing scroll position, and triggering unnecessary recomposition passes for the entire viewport.
Providing a stable, unique key (such as item.id) binds item identity to the underlying data model.
Compose accurately tracks item movement, preserves scroll offsets, and smoothly animates insertions and reorderings using Modifier.animateItem().
The contentType parameter introduces an additional rendering optimization.
In heterogeneous lists with multiple view layouts (like headers, post cards, and banner ads), Compose uses contentType to pool and reuse composition slots.
When an item of a given type scrolls off-screen, Compose reuses its existing layout node structure for a newly entering item of the same contentType, eliminating redundant slot tree construction and layout measurement overhead.

## Interview answer — deep senior

Under the hood, LazyColumn relies on SubcomposeLayout to lazily measure and compose only the items visible within the current viewport plus a configurable prefetch distance.
When key is omitted, the subcomposition mechanism assigns the index integer as the composition key in the SlotTable. When items are inserted, deleted, or reordered, the index mapping fails, causing Compose to dispose of the old SlotTable intervals and allocate completely new ones, discarding any remembered state holders (such as expandable card toggles or inner scroll states) and creating significant garbage collection pressure.
When a stable key is supplied, Compose stores the key inside its ItemProvider. During list mutations, Compose matches the keys across frames, moving existing SlotTable nodes rather than disposing of them.
The contentType parameter operates directly on Compose's node reuse algorithm.
When an item scrolls out of bounds, its SubcomposeSlot is moved to an internal recycling cache.
Without contentType, Compose has no knowledge of whether the next entering item shares the same composable hierarchy; if the next item has a completely different layout (e.g., recycling a simple Header slot for a complex multi-layered VideoCard), Compose must tear down the entire slot subtree and rebuild it from scratch.
With contentType, Compose queries the cache for a slot matching that exact content type identifier, reusing the pre-existing node structure and executing only a fast recomposition of modified text and images.
This mirrors the efficiency of RecyclerView.RecycledViewPool, eliminating frame drops during rapid list flings.

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
