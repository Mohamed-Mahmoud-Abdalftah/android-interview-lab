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

عندما يعود موضع التمرير (Scroll Position) في `LazyColumn` إلى البداية بعد تحديث البيانات (Data Refresh): ما الذي يجب فحصه؟

1. الأسباب الجذرية لإعادة ضبط موضع السكرول (Scroll Reset):
   - **غياب المفاتيح الثابتة (`key` Parameter)**: إذا لم توفر مفتاحاً ثابتاً، يعتمد Compose على الـ Index. إذا استبدلت القائمة بالكامل بكائنات جديدة، يعتقد Compose أن كل شيء جديد ويعيد التعيين للصفر.
   - **توليد كائنات IDs جديدة في كل Refresh**: إذا كانت الـ Data Classes تولد معرفات مؤقتة (مثل `UUID.randomUUID()` أو `System.currentTimeMillis()`) في كل مرة يتم فيها عمل Refresh، تتغير كل الـ Keys فيفقد الـ Scroll موقعه تماماً!
   - **إفراغ القائمة المؤقت (Transient Empty List)**: أثناء عملية الـ Refresh، يقوم الكود بنشر `emptyList()` أو الانتقال لحالة `UiState.Loading` التي تمحو الـ `LazyColumn` من الشاشة لحظياً! عند زوال الـ LazyColumn تتدمر الـ `LazyListState` ويعود السكرول للصفر عند ظهور القائمة الجديدة!

2. ما الذي يجب فحصه وإصلاحه؟
   - **فحص استقرار الـ Keys**: التأكد من استخدام معرفات ثابتة من قاعدة البيانات/السيرفر (`key = { it.serverId }`).
   - **الحفاظ على القائمة أثناء التحميل (Retain List During Refresh)**: عدم إخفاء الـ LazyColumn أثناء التحديث؛ بل إظهار مؤشر سحب (`PullRefreshIndicator` أو شريط علوي) مع إبقاء القائمة السابقة معروضة في مكانها.
   - **الاحتفاظ بالـ `LazyListState` في الـ ViewModel أو عبر `rememberSaveable`**.

## Practical walkthrough

حل مشكلة فقدان موضع السكرول عبر الحفاظ على القائمة والمفاتيح المستقرة أثناء التحديث:
```kotlin
// ❌ كود سيء: يفرغ القائمة أثناء التحميل ويستخدم مفاتيح غير مستقرة فيعيد السكرول للصفر:
@Composable
fun BadFeed(uiState: FeedUiState) {
    if (uiState.isLoading) {
        // 💥 إخفاء LazyColumn تماماً يدمر موضع السكرول فوراً!
        CircularProgressIndicator()
    } else {
        LazyColumn {
            items(uiState.items) { item -> /* بدون key! */ }
        }
    }
}

// ✅ كود سليم: إبقاء القائمة ظاهرة أثناء التحديث مع مفاتيح مستقرة:
@Composable
fun GoodFeed(
    items: ImmutableList<FeedItem>,
    isRefreshing: Boolean,
    listState: LazyListState = rememberLazyListState()
) {
    Box {
        // تظل القائمة موجودة في الـ Composition فلا يفقد listState موضعه إطلاقاً:
        LazyColumn(state = listState) {
            items(
                items = items,
                key = { it.stableId } // مفتاح دائم من قاعدة البيانات
            ) {
                FeedCard(it)
            }
        }
        if (isRefreshing) {
            LinearProgressIndicator(modifier = Modifier.fillMaxWidth().align(Alignment.TopCenter))
        }
    }
}
```

## Why it matters and how it works

Scroll state tracks index and offset, and lazy item keys can help maintain logical position when data changes. A `rememberLazyListState` bound to a removed composition location is recreated. An effect that scrolls on every dataset update overrides remembered position. If a refreshed data set has different identity or sort order, preserving the same index may be semantically wrong even when technically possible.

## Worked example

A feed inserts three newer posts above a user reading post ID 42. Stable post IDs allow the reader to remain anchored near post 42; a root `key(refreshToken)` recreates the entire list state and jumps to top. Remove that root key, keep one list state for the destination, and scope a top-scroll effect only to an explicit new search filter, not every refresh emission.

### Compose/Kotlin walkthrough

```kotlin
@Composable
fun Feed(posts: List<PostUi>, queryIdentity: String) {
    val listState = rememberLazyListState()
    var previousQuery by rememberSaveable { mutableStateOf(queryIdentity) }
    LaunchedEffect(queryIdentity) {
        if (previousQuery != queryIdentity) listState.scrollToItem(0)
        previousQuery = queryIdentity
    }
    LazyColumn(state = listState) {
        items(posts, key = PostUi::id) { post -> PostRow(post) }
    }
}
// Imports: foundation.lazy.LazyColumn/items/rememberLazyListState,
// runtime.LaunchedEffect/rememberSaveable/mutableStateOf/getValue/setValue.
// Refresh under the same query leaves scroll untouched.
```

## Trade-offs and decision criteria

Maintaining position is good for incremental refresh but may confuse users when a new query replaces the dataset. A deliberate top reset on filter change should be explicit. Holding list state too high can carry an old feed's offset into a different account. Stable keys incur little complexity when domain IDs exist.

## Failure modes

Index keys cause row-local state to jump. `rememberLazyListState()` is inside a condition that disappears during Loading. A LaunchedEffect keyed by the whole list calls `animateScrollToItem(0)` after every refresh. Backend IDs change across responses, defeating item identity. Saveability is assumed even though the destination is fully removed from back stack.

## Production perspective

Test refresh insertions above viewport, deletion of current item, query/account switch, navigation return and process recreation. Record first visible ID and offset before/after to distinguish item anchoring from index behavior.

## Interview answer — short

If scroll resets on refresh, inspect three culprits: missing or unstable `key` parameters (e.g. random UUIDs), temporary emissions of an empty list during refresh that resets `firstVisibleItemIndex` to 0, or replacing the `LazyColumn` with a full-screen loading spinner that unbinds `LazyListState` from composition.

## Interview answer — structured

A scroll position resetting to index 0 after a data refresh stems from state lifecycle disconnections or unstable identity mapping.

1. **Transient Empty List Emission**: The most frequent architectural flaw is emitting `emptyList()` or an empty state when a refresh begins. If `LazyColumn` receives an empty list, its viewport collapses to 0 items, instantly resetting `LazyListState.firstVisibleItemIndex` to 0. When the refreshed data arrives a moment later, the list remains at the top.

2. **Unmounting the LazyColumn (Screen-level Loading)**: If the UI replaces the `LazyColumn` with a full-screen `CircularProgressIndicator()` while `isRefreshing` is true, the `LazyColumn` is completely unmounted from the composition tree. Its underlying `LazyListState` loses its layout connection, resetting upon re-entry.

3. **Unstable or Ephemeral Keys**: If items lack keys or use transient generators (like generating new IDs during DTO mapping), Compose treats incoming items as completely novel instances, discarding prior scroll offsets.

## Interview answer — deep senior

Under the hood, `LazyListState` tracks two core integers: `firstVisibleItemIndex` and `firstVisibleItemScrollOffset`. When a new list is bound, Compose's `LazyLayoutItemAnimator` attempts to match existing viewport items to the new list using their `key`. If the key of the top-visible item is found anywhere in the new list, Compose adjusts the scroll offset to keep that exact item pinned to the screen.

To properly implement pull-to-refresh without scroll resets:
- Never clear the existing data list in the ViewModel during a refresh; set an auxiliary boolean `isRefreshing = true`.
- Keep the `LazyColumn` persistently composed and wrap it with `PullToRefreshBox` (Material 3) or place an overlay loading indicator at the top.
- Always declare `key = { it.id }` using immutable persistent database IDs.

## How to answer in the interview

- **Why:** position has both state-owner and item-identity components.
- **How:** inspect listState site, stable keys, and explicit scroll effects.
- **Trade-off:** a new query may intentionally reset to top.
- **Failure case:** regenerated IDs or root key recreate scroll state.
- **Production solution:** test insertion above viewport and a true query change separately.

## Deep-dive talking points

Cover LazyListState ownership, item keys, refresh semantics, explicit scroll commands, and restoration tests.

## Follow-up questions

- **Interviewer:** "How does `LazyListState` keep the viewport pinned when items are added above the visible item?"
  **Answer:** "When stable keys are provided, `LazyListState` tracks the key of the top visible item. If new items are inserted above it, Compose automatically adjusts `firstVisibleItemIndex` so the currently viewed item remains stationary on screen."

- **Interviewer:** "Can you preserve scroll position across process death?"
  **Answer:** "Yes. `rememberLazyListState()` uses `rememberSaveable` internally, saving `firstVisibleItemIndex` and scroll offset into the saved instance bundle automatically."

## Self-check rubric

Distinguish three causes, propose one measurement, and define refresh versus new-query behavior.

## References and reviewed-on date

- [Lazy lists and grids](https://developer.android.com/develop/ui/compose/lists) — keys and list state.
- [Save UI state in Compose](https://developer.android.com/develop/ui/compose/state-saving) — saveable state.

Technically reviewed against primary documentation on 2026-10-13.
