---
id: "ARC-11"
question: "How do you expose loading, content, empty, and error state?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "B"
phase: 2
priority: "P1"
order: 156
editorial_status: "reviewed"
---

# ARC-11

## Original interview question

How do you expose loading, content, empty, and error state?

## What the interviewer evaluates

Model mutually exclusive loading/content/empty/error states and avoid losing cached content on refresh failure.

## Explanation in Arabic

للشاشة البسيطة، sealed `Loading`, `Content(items)`, `Empty`, `Error(reason)` يخلي الحالات المتنافرة واضحة. لكن offline-first screen عندها cached content مع refresh شغال أو error؛ هنا state مركّبة زي `items + isRefreshing + refreshError` أنسب من sealed واحدة تمنع coexistence. Empty لازم تعني data load ناجح لكن مفيش عناصر، مش network error اتخبى. ViewModel يشتق الحالة من repository stream ويحدد retry action؛ الـUI ترسم فقط. بعد process death ارجع للمصدر الدائم بدل افتراض إن الـViewModel state باقية.

## Why it matters and how it works

UI state should be a complete, renderable snapshot. Choose exclusive cases when states cannot coexist, or orthogonal fields when content and refresh status can coexist. Data source freshness and errors should remain distinguishable.

## Worked example

Illustrative Kotlin model:
```kotlin
data class FeedUiState(
    val items: List<Article> = emptyList(),
    val isInitialLoading: Boolean = true,
    val isRefreshing: Boolean = false,
    val refreshError: String? = null
)
data class Article(val id: String, val title: String)
```
For a no-cache screen, a sealed state can make Loading/Content/Empty/Error mutually exclusive.

## Trade-offs and decision criteria

Sealed cases prevent impossible combinations; a data class supports simultaneous cached content and refresh status. Do not create a giant Boolean matrix without invariants. Decide whether errors replace content or appear alongside it based on product requirements.

## Failure modes

A failed refresh sets `items = emptyList()` and UI shows Empty, losing valid cached content and hiding the outage. Preserve cached items, show a non-destructive refresh error, and test offline/retry paths.

## Production perspective

A news feed observes Room, refreshes in background, and displays stale articles with a visible timestamp when offline. Initial load failure and refresh failure have different UI treatment and retry behavior.

## Interview answer — short

I model loading, content, empty, and error as explicit UI state, but I choose the shape by whether they can coexist. Cached content plus refresh failure is different from an initial-load error, and Empty means a successful empty result.

## Interview answer — structured

For a screen without cached data, a sealed state gives exhaustive Loading, Content, Empty, and Error rendering. In an offline-first screen, content may remain visible while refresh is running or failing, so I use an immutable state with items plus refresh metadata. The ViewModel maps repository data and errors into that snapshot. I do not clear valid content on a network failure or treat an outage as an empty list. Tests cover initial, refresh, offline, and retry paths. I would test the transition from cached content into refreshing and then a failed refresh: the list should remain visible with a recoverable message. A successful empty response has different meaning and should display the empty state.

## Interview answer — deep senior

The key is to model legal combinations, not merely list four labels. A sealed hierarchy is strong when states are exclusive. If a feed can show cached articles during refresh, one `Content` case may include refresh status and a recoverable error; a flat set of booleans without invariants can create nonsense combinations. I distinguish initial loading from background refresh and successful empty data from failure. The data layer remains source of truth; after process death the screen reconstructs from persisted data and reload status. Error text is mapped for the UI without leaking raw exception messages. I test transitions rather than isolated snapshots, especially refresh failing after content and retry succeeding. The design should also account for accessibility and interaction. A screen reader should know when loading completes, and a retry control should be available only when retry is meaningful. The ViewModel owns state production, while the composable renders that state and sends events. I avoid combining `isLoading`, `isEmpty`, and `hasError` booleans without invariants because contradictory combinations become possible. State shape follows legal product states, including whether content can coexist with a refresh error.

## Deep-dive talking points

Compare exclusive and coexisting states; show a cached-content refresh transition; explain why Empty requires successful load.

## Follow-up questions

- [ARC-09](../arc-09/): Is loading a business fact? **Answer:** usually it is UI state about current work.
- [ARC-19](../arc-19/): How do cached items survive refresh failure? **Answer:** keep local source of truth and represent refresh error separately.

## Self-check rubric

Predict UI after initial failure, successful empty response, and failed refresh with cache. Each needs a different state and user action.

## References and reviewed-on date

- [Android UI state holders](https://developer.android.com/topic/architecture/ui-layer/stateholders) — screen UI state.
- [Android offline-first guide](https://developer.android.com/topic/architecture/data-layer/offline-first) — local data during network failure.

Technically reviewed against the linked official Android guidance on 2026-10-11. Conceptual examples are not device-tested.
