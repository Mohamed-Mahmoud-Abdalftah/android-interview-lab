---
id: "FLO-15"
question: "Explain debounce and distinctUntilChanged for search."
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "B"
phase: 1
priority: "P1"
order: 128
editorial_status: "reviewed"
---

# FLO-15

## Original interview question

Explain debounce and distinctUntilChanged for search.

## What the interviewer evaluates

Explain debouncing and equality suppression for search without promising cancellation of server work.

## Explanation in Arabic

في search box، `debounce` تستنى فترة هدوء قبل ما تطلع query، فبتقلل requests أثناء الكتابة. `distinctUntilChanged` تمنع نفس query بعد normalization من إعادة الطلب. بعدها `flatMapLatest` يلغي collection القديمة لما query جديدة تجي. لازم نعالج blank query، loading/error لكل query، ونعرف إن cancel قد لا يوقف HTTP call أو server processing بالفعل.

### Practical walkthrough in Egyptian Arabic

في search box، خلي TextField تعرض الحروف فورًا، وبعدها `debounce` على query Flow عشان تقلل API calls؛ `distinctUntilChanged` تمنع نفس query تتبعت مرتين متتاليتين. ترتيب operators مهم حسب هل trim/normalization قبل distinct. `debounce` ممكن ما تصدرش أي intermediate لو المستخدم يكتب باستمرار؛ لا تستخدمها لحدث لازم يتسجل كله.

## Why it matters and how it works

Order matters: trim/normalize before distinct, debounce before expensive search, then switch latest. Debounce uses time and may delay perceived responsiveness; immediate local suggestions can be separate. `distinctUntilChanged` compares adjacent values, not a cache of all past queries.

## Worked example

JVM/Android-compatible snippet with Flow input and cancellable repository search Flow; coroutines-core is required.

```kotlin
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.FlowPreview
import kotlinx.coroutines.flow.*

@OptIn(FlowPreview::class, ExperimentalCoroutinesApi::class)
fun searchResults(
    typed: Flow<String>,
    search: (String) -> Flow<List<String>>,
): Flow<List<String>> = typed
    .map { it.trim() }
    .debounce(300)
    .distinctUntilChanged()
    .flatMapLatest { q -> if (q.isBlank()) flowOf(emptyList()) else search(q) }
```

## Trade-offs and decision criteria

A 300 ms debounce reduces calls but adds latency; tune with usage metrics. Distinct prevents adjacent duplicates but does not replace response caching. Latest-only results fit search, not required writes. Show local results immediately if UX needs fast feedback.

## Failure modes

Applying distinct before normalization sends duplicate equivalent queries. A non-cooperative search client may complete after cancellation; the flow should still avoid publishing stale results to UI. Collecting twice may trigger duplicate requests if not shared.

## Production perspective

A catalog ViewModel holds query state, applies the pipeline, exposes StateFlow of loading/results/error, and collects with lifecycle awareness. Tests use virtual time to type rapidly, pause, repeat query and deliver a slow old response.

## Interview answer — short

“I normalize input, debounce typing, suppress adjacent duplicate queries, then use flatMapLatest to cancel stale search streams. I handle blank input and errors explicitly and do not assume cancellation undoes work already sent to the server.”

## Interview answer — structured

“`debounce` waits for a quiet interval so each keystroke does not trigger network work. `distinctUntilChanged` prevents adjacent equal normalized queries from repeating, while `flatMapLatest` switches to the newest query and cancels old collection. I choose the delay from UX and API cost, not a universal constant. The UI needs loading and error state tied to a query ID, and the repository should make requests cancellable where possible. Tests advance virtual time to verify exactly which queries are launched.”

## Interview answer — deep senior

“A robust search pipeline begins with semantics: an empty query may show suggestions, normalization defines equivalence, and a late response must never overwrite a newer query. I trim or normalize before equality comparison, debounce only the remote path, and use `flatMapLatest` for stale-result cancellation. The old HTTP request may already be on the wire, so I also associate results with query generation and ensure stale data is ignored. I expose a single state stream from the ViewModel to avoid duplicate cold collections, measure request count and perceived latency, and test rapid typing, backspacing, identical queries, errors and cancellation with virtual time and controlled responses. I would keep local text echo immediate and debounce only the network-facing query stream. `debounce` waits for a quiet interval before forwarding a value, so it reduces request volume while the user types; `distinctUntilChanged` suppresses consecutive equal normalized queries. I decide whether trim and case normalization happen before equality, because that changes what counts as duplicate. Then I use `flatMapLatest` for the request so an old response does not replace a newer query. Debounce introduces latency, which is a product trade-off; a short interval needs testing with real typing behavior and accessibility input. I would test rapid `a`, `ab`, pause, then a repeated `ab`, and verify request count and final UI state.”

## How to answer in the interview

- **Why:** search requests should follow stable intent without slowing text entry.
- **How:** immediate field, normalize, debounce, distinct, latest request.
- **Trade-off:** fewer calls versus result latency.
- **Failure case:** debouncing the field or letting old results win.
- **Production solution:** test request count and rapid typing.

## Deep-dive talking points

Trace operator order, timing, stale response and query-associated UI state.

## Follow-up questions

- [FLO-14](../flo-14/): Why flatMapLatest? **Answer:** it switches away from prior query streams.
- [FLO-24](../flo-24/): How test debounce? **Answer:** use runTest virtual time and controlled fake responses.

## Self-check rubric

Can I justify operator order, distinguish adjacent equality from cache, and handle a late old response?

## References and reviewed-on date

- [Kotlin Flow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/) — debounce and distinctUntilChanged.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
