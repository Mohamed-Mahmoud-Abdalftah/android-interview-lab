---
id: "FLO-01"
question: "What is Flow? Compare Flow and a single suspend function."
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "A"
phase: 1
priority: "P1"
order: 114
editorial_status: "reviewed"
---

# FLO-01

## Original interview question

What is Flow? Compare Flow and a single suspend function.

## What the interviewer evaluates

Distinguish a stream of asynchronous values from a single suspend result, including collection lifetime.

## Concept and technical explanation

A suspending function returns one result or throws; suspension does not imply a background thread. A Flow represents a stream that can emit zero, one, or multiple values, then complete or keep running. A Flow built with `flow {}` is cold: its producer runs separately for each collection. The Flow interface can also refer to hot implementations such as StateFlow and SharedFlow, so coldness is a property of the source, not a guarantee of the type. In a simple unbuffered cold pipeline, upstream emission waits for downstream processing. Operators such as `buffer` and `flowOn` can introduce a channel and change this timing. Cancellation is cooperative and does not instantly stop arbitrary blocking work.

## Practical walkthrough (English)

Conceptual Android sketch (project imports and models omitted; not compiled by the JVM suite):
```kotlin
interface UserAccountRepository {
    // 1. One-shot operation: Suspend function returns a single asynchronous result
    suspend fun updateDisplayName(newName: String): Result<Unit>

    // 2. Continuous data stream: Flow emits multiple values over time as database mutates
    fun observeAccountBalance(): Flow<BigDecimal>
}

// In the ViewModel:
class AccountViewModel(private val repository: UserAccountRepository) : ViewModel() {
    val balance: StateFlow<BigDecimal> = repository.observeAccountBalance()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = BigDecimal.ZERO
        )

    fun changeName(name: String) {
        viewModelScope.launch {
            repository.updateDisplayName(name)
        }
    }
}
```

## Explanation in Arabic

`suspend fun` عقدها إن النداء بيرجع نتيجة واحدة (حتى لو `Unit`) أو يرمي Exception، لكنه ممكن يعلّق من غير ما يمسك Thread. ده مناسب لعملية زي `refreshProfile()` أو كتابة صف في Room.

`Flow<T>` عقد Collection لقيم متتابعة: ممكن المصدر يطلع صفر أو واحدة أو قيم كتير، وينتهي أو يفضل شغال. الـ Flow اللي بتبنيه بـ `flow {}` Cold: الكود اللي جواه بيبدأ مع كل `collect`، فجامعين ممكن يشغّلوا نفس الـ API call مرتين. لكن نوع `Flow` نفسه مش ضمان إنه Cold؛ `StateFlow` و`SharedFlow` أمثلة Hot.

في Pipeline بسيط، `emit` و`collect` بيشتغلوا بالتتابع، و`emit` يقدر يعلّق لحد ما الـ Downstream يخلص. `buffer` و`flowOn` وبعض Operators بتفصل التنفيذ بقناة، فمش صح نقول إن كل Emission بتستنى كل Collector في أي إعداد. الـ Cancellation تعاوني؛ الشغل الـ Blocking لازم يكون قابل للإيقاف أو يتدار بشكل مناسب.

## Practical walkthrough

في شاشة رصيد: `suspend fun refreshBalance()` بتطلب آخر نسخة من السيرفر وترجع نجاح أو خطأ. `fun observeBalance(): Flow<Balance>` من Room بتدي الشاشة الحالة المخزنة، ولما الجدول يتغير تبعت قيمة جديدة. الـ ViewModel ممكن يحوّلها إلى `StateFlow` للـ UI بـ `stateIn` وسياسة Sharing مناسبة. في Views، جمع القيم داخل `repeatOnLifecycle(STARTED)` بيوقفه لما الشاشة تتوقف؛ وفي Compose استخدم Lifecycle-aware Collection. لو Repository عملت Network Request جوه Cold Flow، كل Collection جديدة ممكن تعيد الطلب، فراجع Ownership والـ Sharing.

## Why it matters and how it works

Intermediate operators build a pipeline without starting a cold source; a terminal operation such as `collect` or `first` starts a cold source. Recollecting it may repeat side effects, including network calls. Hot Flow implementations have different sharing and replay contracts. A suspending function can return a Flow, but making the factory suspending is rarely necessary unless creating that Flow itself requires suspending work.

## Worked example

JVM example needs `kotlinx-coroutines-core`; it emits successive local snapshots, not a production database observer.

```kotlin
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

suspend fun oneName(): String = "Mona"
fun names(): Flow<String> = flow {
    emit("Mona")
    emit("Mona Ali")
}
```

## Trade-offs and decision criteria

Use a suspend function when an operation has one result, and Flow when the API contract benefits from observing a sequence over time. A finite one-element Flow can still be valid when stream composition is the intended contract. For shared state, stateIn or shareIn can avoid repeated upstream work, but the scope, sharing policy, and replay behavior must be chosen deliberately.

## Failure modes

Collecting a cold network Flow twice may make two network requests. Collecting indefinitely from UI without lifecycle awareness wastes work offscreen. A plain Flow is not automatically cached or shared.

## Production perspective

A repository exposes `suspend fun refresh()` to trigger one remote fetch and `Flow<List<Item>>` from Room for ongoing local truth. The ViewModel shares state appropriately; the UI collects only while active.

## Interview answer — short

A suspend function returns one result or throws, and may suspend without occupying a thread while waiting. A Flow represents a stream that can emit zero, one, or multiple values over time. A flow built with `flow {}` is cold and runs for each collector; hot Flow implementations such as StateFlow follow different sharing rules. Cancellation is cooperative, and buffering can decouple emission from collection.

## Interview answer — structured

The key difference is the API contract. A suspend function returns one result or throws, making it a clear choice for a one-shot mutation or refresh. A Flow can emit zero, one, or many values over time, which fits an observable Room query.

For example, a repository can expose `suspend fun refreshBalance()` to fetch and store one update and `fun observeBalance(): Flow<Balance>` for ongoing local changes. A Flow built with `flow {}` is cold: each collector starts its producer again. If that producer calls an API, two collectors may create two network calls. StateFlow and SharedFlow are hot sources with different sharing rules.

The UI should collect under an appropriate lifecycle. If a ViewModel converts the source with stateIn, its scope and SharingStarted policy determine how long the upstream remains active. This distinction prevents duplicate work and makes cancellation and test behavior explicit.

## Interview answer — deep senior

A suspend function is a coroutine-aware operation with one return value or an exception; it can suspend without occupying a thread, but it does not automatically switch dispatchers. Flow is an interface for a sequence of values. The `flow {}` builder creates a cold source whose body runs for each collection. StateFlow and SharedFlow are hot implementations, so saying that every Flow is cold is inaccurate.

In a simple cold pipeline, upstream and downstream execute sequentially in the collector context. A slow collector delays `emit` because `emit` is suspending. Operators such as buffer and flowOn can create a channel boundary: upstream can run ahead up to the configured capacity, and flowOn changes the upstream context, not the downstream collector context. Cancellation propagates through suspension points, but blocking calls may need explicit cancellation support and resources still need cleanup.

For Android UI, a Room query Flow can be collected with repeatOnLifecycle in a View screen or an equivalent lifecycle-aware Compose API. Turning it into StateFlow with stateIn changes sharing and replay behavior. It retains state and conflates intermediate values, so it is not a guaranteed event log. Test multiple collectors, lifecycle restart, error paths, and whether a cold network source accidentally repeats an HTTP request.

## How to answer in the interview

- **Why:** a one-shot result and a changing source have different contracts.
- **How:** show cold collection and a Room observer.
- **Trade-off:** sharing saves duplicate work but adds scope and replay policy.
- **Failure case:** two collectors duplicate a network call.
- **Production solution:** separate refresh from observation and test lifecycle restart.

## Deep-dive talking points

Trace lazy operators, terminal collection, multiple collectors and the transition to a hot shared stream.

## Follow-up questions

- **Interviewer:** "Is every Flow cold?"
  **Answer:** "No. `flow {}` builds a cold source and runs per collection, but StateFlow and SharedFlow are hot Flow implementations."

- **Interviewer:** "Does emit always wait for the collector?"
  **Answer:** "In a simple unbuffered pipeline, downstream work delays upstream emission. Buffering and flowOn can decouple execution, so capacity and overflow behavior matter."

- **Interviewer:** "Can a suspend function return a Flow?"
  **Answer:** "Yes. The factory usually need not suspend if it just constructs a cold pipeline, but the type system does not prohibit it; choose the API based on when real work must begin."

## Self-check rubric

Can I choose single versus stream, identify a terminal operator, predict two collectors and name an Android lifecycle owner?

## References and reviewed-on date

- [Kotlin Flow guide](https://kotlinlang.org/docs/flow.html) — cold builders and operators.
- [Flow API contract](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/) — cold and hot implementations.
- [Android StateFlow and SharedFlow](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow) — sharing and lifecycle collection.

Technically reviewed against primary documentation on 2026-10-19.
