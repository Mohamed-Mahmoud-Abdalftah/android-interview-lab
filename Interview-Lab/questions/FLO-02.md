---
id: "FLO-02"
question: "Explain cold flows and what happens with multiple collectors."
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "A"
phase: 1
priority: "P1"
order: 115
editorial_status: "reviewed"
---

# FLO-02

## Original interview question

Explain cold flows and what happens with multiple collectors.

## What the interviewer evaluates

Predict repeated execution for two cold-flow collectors and choose sharing deliberately.

## Concept and technical explanation

A flow created with `flow { ... }` is cold: constructing its pipeline does not run the builder, and each terminal collection starts a separate upstream execution. Two collectors of the same cold flow object can therefore run two API calls or register two callbacks if those effects are inside the upstream. The `Flow` interface itself does not imply coldness: `StateFlow` and `SharedFlow` implement it and are hot. An external cache can also mean two upstream invocations do not become two physical HTTP requests. Use `shareIn` or `stateIn` when concurrent consumers should share an active upstream; configure the owning scope, start policy, replay, and session lifetime deliberately.

## Practical walkthrough (English)

A cold builder runs once per collection; this conceptual example assumes `api` is an application dependency.

```kotlin
fun price(symbol: String): Flow<Double> = flow {
    println("starting upstream for $symbol")
    emit(api.getLatestPrice(symbol))
}

suspend fun observeTwice() = coroutineScope {
    val source = price("BTC")
    launch { source.collect { println("A: $it") } }
    launch { source.collect { println("B: $it") } }
    // The builder starts twice. Whether HTTP goes out twice depends on api caching.
}
```

## Explanation in Arabic

الـ cold Flow معناه إن **المنتِج** ما يبدأش شغله غير لما حد يجمعه. في `flow { ... }`، الكود جوّه الـ builder ما بيتنفّذش عند إنشاء المتغير؛ أول `collect` يشغّله، وجمع تاني لنفس المرجع يشغّله من البداية بشكل مستقل. لو الكود جوّه بينادي API أو بيسجّل listener، التكلفة دي ممكن تتكرر لكل collector.

خلي بالك من فرق مهم في المقابلة: `Flow<T>` واجهة عامة، ومش كل كائن من نوعها cold. `StateFlow` و`SharedFlow` كمان `Flow` لكنهم hot. والحكم على عدد طلبات HTTP الفعلية يحتاج معرفة هل فيه cache تحت الـ Flow.

لو محتاج مشتركين يشوفوا نفس تشغيل upstream، استخدم `shareIn` لبث قابل لضبط `replay`، أو `stateIn` لأحدث حالة وقيمة ابتدائية. اختار scope يخص صاحب الداتا وسياسة `SharingStarted` مناسبة؛ `WhileSubscribed` ممكن يوقف المصدر ويشغّله من جديد بعد ما كل المشتركين يمشوا.

## Practical walkthrough

جرّب عدادًا داخل المصدر عشان تشوف الفرق:
```kotlin
var starts = 0
val cold = flow {
    starts++
    emit(repository.loadPrice())
}
cold.first()
cold.first()
check(starts == 2) // الـ builder اتشغّل مرتين
```
لو `loadPrice()` عنده cache، قد تلاقي نداءي Kotlin لكن طلب شبكة واحد. ولشاشة فيها أكتر من مستهلك للحالة:
```kotlin
sealed interface PriceUiState {
    data object Loading : PriceUiState
    data class Ready(val price: Double) : PriceUiState
}
val uiSource: Flow<PriceUiState> = cold.map { PriceUiState.Ready(it) }
val priceState = uiSource.stateIn(
    scope = viewModelScope,
    started = SharingStarted.WhileSubscribed(5_000),
    initialValue = PriceUiState.Loading
)
```
اختبر إن المشتركين المتزامنين بيشوفوا نفس التشغيل. بعد اختفاء آخر مشترك وانتهاء المهلة، توقع احتمال تشغيل جديد لما الشاشة ترجع.

## Why it matters and how it works

Intermediate operators over a cold source stay lazy. Each collection independently executes the source unless it is hot or an external layer coalesces work. `shareIn` creates a sharing coroutine in the supplied scope; `stateIn` also provides a current value. `SharingStarted.WhileSubscribed` may stop and later restart that upstream, so sharing does not promise exactly one execution forever.

## Worked example

JVM example uses `kotlinx-coroutines-core`; `calls` increments once per collection, illustrating duplicate upstream execution.

```kotlin
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.toList

suspend fun demo(): Int {
    var calls = 0
    val cold = flow { calls++; emit(calls) }
    cold.toList()
    cold.toList()
    return calls // 2
}
```

## Trade-offs and decision criteria

Sharing saves duplicate subscriptions but introduces scope lifetime, replay and freshness decisions. Do not share a user-specific stream in an application scope without session invalidation. A cached repository source may already prevent duplicated HTTP even if its Flow is cold; inspect the implementation.

## Failure modes

Two composables independently collecting a cold refresh Flow can cause duplicate API calls. A shared stream can also outlive logout and replay another user’s state if scoped incorrectly. Choose the owner and reset policy explicitly.

## Production perspective

A Room DAO Flow may run separate observations for two collectors; a ViewModel uses `stateIn(viewModelScope, WhileSubscribed(...), initial)` to expose a single UI state. The app must replace or invalidate user-specific ViewModel state and caches on a session switch.

## Interview answer — short

A cold producer such as `flow { ... }` runs its upstream separately for each collection. Two collectors can repeat a network call or listener registration, although an underlying cache can change the number of actual HTTP requests. `Flow` is an interface, not a coldness guarantee. Share an expensive upstream with `shareIn` or `stateIn` when the scope and replay policy fit.

## Interview answer — structured

Start with the producer. Constructing `flow { emit(api.load()) }` does not invoke `api.load()`. Collecting it twice invokes the builder twice, even when both collectors hold the same Flow reference. A cold `callbackFlow` can likewise register one callback per collection. This is useful when each consumer needs a fresh, independent run; it can be costly when several UI consumers need the same data.

The type `Flow<T>` alone cannot settle the question because `StateFlow` and `SharedFlow` are hot implementations. When sharing is appropriate, `shareIn` multicasts one active upstream execution, while `stateIn` also retains a current state. Pick a scope owned by the data and specify `SharingStarted` and replay. Under `WhileSubscribed`, upstream can restart after all collectors leave; measure behavior rather than promising a single request forever.

## Interview answer — deep senior

The key diagnostic is where the side effect lives. For `flow { ... }`, each terminal collection invokes the upstream block independently. Two collectors can therefore open two listeners or call a repository function twice. Whether this becomes two physical database queries or HTTP requests depends on the repository, cache, and source implementation. A `callbackFlow` that registers a platform listener in its block typically registers one listener per collection and should unregister each with `awaitClose` on cancellation.

`Flow` is a common interface, not a cold-stream marker. `StateFlow` and `SharedFlow` implement it but their producer and storage are not recreated per collector. To share a cold upstream, `shareIn(scope, started, replay)` and `stateIn(scope, started, initialValue)` launch a sharing coroutine. They have distinct contracts: StateFlow offers a current value, while SharedFlow offers configurable replay. `WhileSubscribed` can stop upstream when subscribers disappear and start it again later; its stop timeout and replay expiration affect freshness and cost. A long-lived scope holding user-specific replay needs explicit invalidation on logout.

For Android UI I collect with `repeatOnLifecycle` or `collectAsStateWithLifecycle`, then test both simultaneous subscribers and a STOP/START gap. I instrument starts inside the builder, and separately measure actual network traffic when a cache exists. That tells me whether sharing is needed and whether the chosen scope really represents the data lifetime. It also separates proven duplicate source execution from assumptions about transport behavior.

## How to answer in the interview

- **Why:** multiple consumers can multiply upstream cost.
- **How:** count builder starts under two collectors.
- **Trade-off:** cold freshness versus shared lifecycle.
- **Failure case:** assuming one Flow instance means one network request.
- **Production solution:** share only when ownership and replay semantics are explicit.

## Deep-dive talking points

Compare per-collector side effects, external caches, sharing scope and stale replay on session change.

## Follow-up questions

- **Interviewer:** "Can a cold `flow {}` produce values with no collector?"
  **Answer:** "Its builder does not run until a terminal collection. External services or caches may still do other work; this says nothing about all CPU activity in the app."
- **Interviewer:** "How do you test duplicate upstream work?"
  **Answer:** "Increment a counter inside the builder, collect twice under `runTest`, and assert two starts. Measure actual HTTP calls separately if the repository caches."
- **Interviewer:** "Is every `Flow<T>` cold?"
  **Answer:** "No. `StateFlow` and `SharedFlow` are hot `Flow` implementations. Inspect the producer and sharing operators."

## Self-check rubric

Can I predict subscription count, choose sharing, and identify its scope and replay risk?

## References and reviewed-on date

- [Kotlin Flow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/) — cold collection.
- [Kotlin shareIn API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/share-in.html) — shared upstream.

- [Kotlin stateIn API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/state-in.html) — current-state sharing and start policy.

Technically reviewed against primary documentation on 2026-10-19.
