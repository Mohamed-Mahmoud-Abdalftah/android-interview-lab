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

## Concept and technical explanation

When a LazyColumn's scroll position unexpectedly resets to index zero after a data refresh, it indicates a violation of list identity or state preservation across composition cycles. The primary culprit is omitting stable keys in the items() block, causing Compose to rely on fluctuating list indices that reset when items are prepended, sorted, or replaced. The second major culprit is re-instantiating the LazyListState by placing rememberLazyListState() inside a conditional composable branch (such as if (isLoading) LoadingView() else LazyColumn()) that disposes of the state holder when loading toggles. Engineers resolve this by providing unique stable keys and hoisting LazyListState above conditional branches.

## Practical walkthrough (English)

Diagnosing and fixing LazyColumn scroll reset regressions:
```kotlin
// ❌ REGRESSION 1: Conditional branch destroys LazyListState on refresh!
// When isRefreshing is true, LazyColumn is unmounted, destroying its remembered scroll state!
@Composable
fun BadRefreshableList(isRefreshing: Boolean, items: List<Item>) {
    if (isRefreshing) {
        LoadingSpinner() // LazyColumn is destroyed! Scroll position is lost forever!
    } else {
        // ❌ REGRESSION 2: Missing stable keys! Index reset happens on new dataset emission!
        LazyColumn {
            items(items) { item -> ItemCard(item) }
        }
    }
}

// ✅ FIXED: Hoist state, provide stable keys, and overlay loading indicators!
@Composable
fun SafeRefreshableList(
    isRefreshing: Boolean,
    items: List<Item>,
    listState: LazyListState = rememberLazyListState() // State preserved across refreshes!
) {
    Box(modifier = Modifier.fillMaxSize()) {
        LazyColumn(state = listState) {
            items(
                items = items,
                key = { it.id }, // STABLE KEY: Preserves exact scroll offset across data updates!
                contentType = { "ITEM_TYPE" }
            ) { item ->
                ItemCard(item)
            }
        }

        // Overlay refresh indicator instead of tearing down the LazyColumn!
        if (isRefreshing) {
            CircularProgressIndicator(modifier = Modifier.align(Alignment.TopCenter))
        }
    }
}
```

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

To fix scroll position resets after a refresh, inspect two critical areas. First, verify that items() has a unique stable key (key = { it.id }); without stable keys, dataset mutations cause Compose to lose track of items and reset scroll to zero. Second, check if LazyColumn is wrapped in a conditional branch like if (isLoading) which unmounts the list and destroys rememberLazyListState(). We fix this by supplying stable keys, hoisting LazyListState, and overlaying loading spinners instead of destroying the list.

## Interview answer — structured

A LazyColumn scroll position resetting to the top upon refreshing data is one of the most frustrating user experience bugs in Android apps.
When diagnosing this regression, senior engineers systematically inspect two primary architecture failure points.
Failure point one is the absence of unique stable keys inside items().
When the key parameter is omitted, LazyColumn uses the item's integer index as its identity.
If a data refresh prepends a single item or alters the list sorting order, index zero now maps to a completely different item.
Compose cannot correlate old items with new items, discarding internal scroll offset calculations and resetting the viewport to the top.
Providing key = { it.id } binds scroll position directly to the persistent item identity.
Failure point two is state destruction caused by conditional composition branching.
A common anti-pattern is writing: if (state.isLoading) LoadingScreen() else LazyColumn().
When a pull-to-refresh occurs, isLoading flips to true.
Compose unmounts the entire LazyColumn subtree, instantly purging the remembered LazyListState from the SlotTable.
When loading completes, Compose instantiates a brand-new LazyListState initialized to index zero.
To resolve this, engineers keep the LazyColumn mounted continuously—overlaying the progress indicator via a Box—and hoist LazyListState above transient loading states.

## Interview answer — deep senior

Under the hood, LazyColumn scroll maintenance is mediated by LazyListState and its internal LazyListScrollPosition tracker.
LazyListScrollPosition stores two values: the index of the first visible item and the exact pixel scroll offset.
When a stable key is supplied, LazyListScrollPosition registers a key-to-index mapping inside its internal ItemProvider.
When a data flow emits a new immutable list, the Lazy layout pipeline executes a measure pass.
It queries the ItemProvider for the new index of the previously pinned stable key.
If an item was prepended at index 0, the pinned key's index shifts from 0 to 1, and Compose adjusts the scroll position synchronously by updating the anchor index without jumping.
If keys are omitted, the ItemProvider defaults to position integers; any dataset shift invalidates the anchor, forcing the scroll position to fall back to index 0.
Regarding conditional branching, rememberLazyListState() registers an entry in the local SlotTable.
When an if (isLoading) branch swaps out LazyColumn, the Composer executes an unmount pass, invoking dispose() on the RecomposeScope and releasing the SlotTable interval.
Even if rememberSaveable is used, if the composable leaves the composition entirely without a preserved SaveableStateHolder key, the in-memory state is cleared.
Maintaining the LazyColumn in the composition hierarchy and toggling loading indicators through Box overlays or SwipeRefresh containers preserves the SlotTable intact, securing seamless scroll retention across high-frequency network refreshes.

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
