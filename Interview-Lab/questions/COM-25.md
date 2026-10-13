---
id: "COM-25"
question: "A user taps Save twice while a request is in flight. How do you make UI and domain behavior safe?"
topic: "Jetpack Compose"
code: "COM"
group: "C"
phase: 3
priority: "P1"
order: 254
editorial_status: "reviewed"
---

# COM-25

## Original interview question

A user taps Save twice while a request is in flight. How do you make UI and domain behavior safe?

## What the interviewer evaluates

- Address UI feedback and domain/server idempotency separately.
- Handle concurrency races, retry and process death.
- Define persisted result and unknown outcome reconciliation.

## Explanation in Arabic

في UI اعرض `Saving` وعطّل زر Save أو امنع taps إضافية، لكن لا تعتبر هذا ضمانًا: callbacks قد تصل مرتين، screen تتعاد، أو request يعاد بعد timeout. ViewModel/use case يعمل single-flight أو state machine يرفض transition ثانية لنفس العملية. لو Save يكتب محليًا، transaction/unique key تمنع duplicate. لو API مالية أو create operation، استخدم idempotency key ثابت لنفس intent والـserver يطبّقه ويرجع نفس النتيجة؛ عند timeout لا تفترض الفشل بل استعلم عن status. بعد process death استعد pending operation من durable source حسب أهمية العملية.

## Practical walkthrough

تعطيل Save في UI يحسن التجربة، بس مش ضمان ضد event متكرر أو retry بعد timeout. الـViewModel يحرس transition لـSubmitting؛ والـserver يستخدم idempotency key ثابت لنفس العملية. لو الاتصال وقع بعد commit، اسأل عن status أو أعد بنفس key، ما تنشئش عملية جديدة. لو timeout حصل بعد commit على السيرفر، إظهار “فشل” قطعي أو key جديدة ممكن يعمل duplicate. احفظ operation ID واتأكد من status؛ UI disabled مجرد أول طبقة حماية.

## Why it matters and how it works

Compose rendering can disable a control from state, but event delivery and network retries are independent of rendering. A mutex or atomic state transition protects one in-process owner, while server idempotency protects across devices, process restarts and retries. Distinguishing a new user intent from retry of the same intent determines whether to reuse the key.

## Worked example

A checkout screen submits an order with `clientOperationId`. The button enters `Submitting`, and the ViewModel ignores another tap for that ID. The backend stores idempotency key plus request fingerprint and returns the same order on retry. If connection drops after server commit, the app queries order status and shows Pending rather than creating a second order.

### Compose/Kotlin walkthrough

```kotlin
// Inside SaveViewModel: _ui is MutableStateFlow<SaveUiState>; Draft has a
// persisted operationId; repository/server honor that ID idempotently.
private val saveMutex = Mutex()
fun save(draft: Draft) = viewModelScope.launch {
    if (!saveMutex.tryLock()) return@launch
    try {
        _ui.update { it.copy(saving = true) }
        try {
            val id = repository.save(draft, operationId = draft.operationId)
            _ui.update { it.copy(saving = false, savedId = id) }
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            _ui.update { it.copy(saving = false, error = "Save status unknown") }
        }
    } finally { saveMutex.unlock() }
}
// Imports: kotlinx.coroutines.sync.Mutex, kotlinx.coroutines.flow.update,
// kotlinx.coroutines.CancellationException. Reconcile uncertain server status.
```

## Trade-offs and decision criteria

Disabling the button is simple UX but insufficient correctness. A local mutex prevents one process race but not post-crash duplicates. Server idempotency requires storage and expiry policy; high-value writes justify it. A generic `debounce` can drop a legitimate second intent, so define operation identity explicitly.

## Failure modes

Two rapid callbacks pass a non-atomic `if (!saving)` check. Timeout is treated as failure and a new key creates a duplicate charge. The UI shows success before server confirmation. An operation key is reused for a changed payload, causing incorrect deduplication.

## Production perspective

Test rapid double tap, retry after timeout, app restart, duplicate server delivery and mismatched payload. Log operation IDs without secrets and expose an explicit pending/reconciliation state. Make saved-state and backend contracts agree.

## Interview answer — short

“I disable duplicate UI input, enforce a single operation transition in the owner, and use durable/server idempotency for writes that can be retried after a crash. Disable Save for feedback, then enforce one operation in domain and server layers.”

## Interview answer — structured

“The UI should show Saving and prevent repeat taps, but I do not rely on the button for correctness. The ViewModel or use case atomically rejects a second submission for the same operation, and storage/server applies a stable idempotency key. A timeout is an unknown outcome, so I query status or retry with the same key rather than issuing a new create. I test double taps, delayed responses and process recreation. A stable operation ID lets a retry after timeout ask about the same save instead of creating a second one.”

## Interview answer — deep senior

“I separate user feedback from the invariant ‘one intent creates at most one result.’ Compose receives a `Submitting` state that disables Save and shows progress, but two callbacks can still race before a frame updates. The ViewModel or use case owns an atomic single-flight transition keyed by an operation ID. For a local write I use a transaction or unique constraint; for a network create or payment I send an idempotency key whose scope and request fingerprint the server enforces. A retry of the same intent reuses that key, while an intentionally new save gets a new one. If the request times out after the server commits, the status is unknown; I reconcile with the server instead of displaying definite failure and creating another operation. For high-value work I persist enough pending metadata to recover after process death and avoid storing sensitive payloads casually. I test rapid taps, retries, server duplicate delivery, changed payload under the same key, and late results after navigation. The button state improves experience; domain and server contracts provide safety. I treat timeout as an unknown outcome and reconcile with the server before reporting definite failure.”

## How to answer in the interview

- **Why:** disabling the button does not prevent duplicate domain work.
- **How:** guard in process and reuse an idempotency key across retries.
- **Trade-off:** key lifetime and request fingerprint need server agreement.
- **Failure case:** timeout after commit causes duplicate order.
- **Production solution:** query status and persist pending operation where needed.

## Deep-dive talking points

Discuss atomic single-flight, idempotency keys, payload fingerprints, unknown outcomes, and recovery.

## Follow-up questions

- Is a disabled button enough? **Answer:** no; events, retries and process restarts bypass that UI guard.
- What does a timeout mean? **Answer:** outcome may be unknown; query or retry with the same operation identity.
- When should a new key be created? **Answer:** for a genuinely new user intent, not a retry of the same write.

## Self-check rubric

Name UI, in-process and server guards; explain timeout reconciliation and tests.

## References and reviewed-on date

- [Compose state architecture](https://developer.android.com/develop/ui/compose/architecture) — state-driven UI.
- [WorkManager persistent work](https://developer.android.com/topic/libraries/architecture/workmanager) — durable retries where applicable.
- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests) — provider-specific idempotency example.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Server key policy must match the actual API contract.
