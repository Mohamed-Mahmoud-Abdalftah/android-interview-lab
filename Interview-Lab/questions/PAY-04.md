---
id: "PAY-04"
question: "What risks arise when a local payment record is not durably committed?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "A"
phase: 5
priority: "P2"
order: 474
editorial_status: "reviewed"
---

# PAY-04

## Original interview question

What risks arise when a local payment record is not durably committed?

## What the interviewer evaluates

- Write-ahead intent before an external financial side effect.
- Crash windows, database durability and server reconciliation.

## Explanation in Arabic

لو terminal بعت authorization قبل ما يحفظ operation ID وstatus بشكل durable، البطارية ممكن تفصل بعد issuer approval وقبل كتابة السجل؛ بعد restart التطبيق ما يعرفش يسأل عن العملية أو يعكسها. لذلك نسجل intent والهوية والparameters الآمنة في transaction محلية قبل الإرسال، ثم نحدّث state atomically حسب الرد. الحفظ المحلي وحده مش كفاية لو الدليل ضاع؛ backend/provider reconciliation لازم موجود.

### Practical walkthrough in Egyptian Arabic

افترض الجهاز فصل بين `sendAuthorization()` و`insertAttempt()`: issuer ممكن يكون وافق لكن local DB فاضية. الحل write-ahead intent قبل النداء الخارجي، وبعد restart افحص كل محاولة غير نهائية. حتى مع Room transaction، DB محلية والـprovider نظام تاني؛ مفيش atomic commit بينهم، فbackend ledger لازم تكشف الفجوات.

## Why it matters and how it works

A database transaction protects related local rows, but cannot atomically commit with a remote payment provider. This is a distributed-systems gap. A write-ahead intent plus stable server operation ID narrows the gap; authoritative status lookup and reconciliation close unknown outcomes after crashes.

## Worked example

Before calling the SDK, Room writes `PaymentAttempt(id, amountMinor, state=READY)` and any required reversal obligation in one transaction. After sending, it records PROCESSING/UNKNOWN/FINAL. On startup, a worker scans nonfinal attempts and queries the backend using the same ID; it never blindly reissues a new charge.

### Kotlin/Android sketch

```kotlin
// Repository sketch: intent is committed before external I/O.
suspend fun authorize(intent: PaymentAttempt): PaymentState {
    attempts.insertIfAbsent(intent.copy(state = PaymentState.Initiated))
    val result = try { gateway.authorize(intent.operationId, intent.amountMinor) }
        catch (e: IOException) { GatewayResult.Unknown }
    return attempts.applyEvidence(intent.operationId, result)
}
// The DB write, gateway, and applyEvidence are separate steps;
// recovery scans nonfinal rows. Imports: java.io.IOException.
// App-owned PaymentAttempt/GatewayResult/DAOs; do not catch cancellation.
```

## Trade-offs and decision criteria

Synchronous durable writes may add latency; unsafe asynchronous writes reduce latency but risk lost evidence. Choose durability guarantees consciously and test power-loss behavior on representative hardware. Local DB corruption still needs backend recovery.

## Failure modes

Using `SharedPreferences.apply()` right before SDK call does not guarantee a durable commit before power loss. Even a Room transaction may not cover external provider effects. Persist before send and reconcile after any ambiguous window.

## Production perspective

Production defines write ordering, fsync/durability assumptions, backend transaction records, startup recovery, and support escalation for unresolvable IDs. Test forced process kill and battery removal at each state boundary.

## Interview answer — short

“I commit a write-ahead payment attempt before calling the SDK. If power fails later, the stable ID lets me look up and reconcile; a Room transaction cannot make the remote authorization atomic.”

## Interview answer — structured

“The dangerous window is issuer approval followed by terminal power loss before local save. I record a stable operation ID and immutable request data durably before sending, then update status transactionally. After restart, I scan nonfinal attempts and query the backend/provider rather than guess failure or issue a new charge. Local atomicity protects local rows, but it cannot create a distributed atomic commit with the provider; reconciliation is essential. This is a distributed-systems gap. The critical ordering is commit intent, call the SDK, then record evidence.”

## Interview answer — deep senior

“I write a state-transition and crash-point table around every external call. A durable write-ahead record exists before the first network/SDK side effect. That record includes safe identifiers and the operation’s immutable parameters, not PAN/PIN. If a response arrives, I commit status and any reversal obligation atomically; if the process dies anywhere, recovery resumes from persisted state and asks authority. I test actual kill/power loss timing because SQLite transaction completion and storage durability have platform/hardware constraints. The backend retains its own operation log, and operations handles discrepancies that automatic reconciliation cannot resolve. After sending, it records PROCESSING/UNKNOWN/FINAL. I would power-cycle the terminal after the remote call and prove that the original ID still supports lookup. The important crash matrix has four points: before local intent commit, after commit but before send, after remote authorization but before response, and after response but before final local write. The first should not reach the provider by construction. The second can be resumed under the same ID. The last two are Unknown locally until an authoritative lookup resolves them. Room can atomically protect local rows, but it cannot create a distributed transaction with an acquirer. I would require the backend to keep an independent operation ledger and run reconciliation against provider records, especially when local storage is damaged or the device is lost. Tests must kill the process at each boundary.”

## How to answer in the interview

- **Why:** local loss destroys the reference needed for recovery.
- **How:** durably write identity and safe parameters before external I/O.
- **Trade-off:** local atomicity cannot cover a remote issuer.
- **Failure case:** power loss after remote approval but before local final write.
- **Production solution:** startup scan plus backend/acquirer reconciliation.

## Deep-dive talking points

Prompt for write-ahead record, distributed atomicity gap, startup scanner, safe metadata and power-loss tests.

## Follow-up questions

- [PAY-06](../pay-06/): What local writes must be atomic? **Answer:** status and reversal obligation.
- [PAY-12](../pay-12/): What if approval preceded local save? **Answer:** server/provider ledger must recover the transaction.

## Self-check rubric

Can I identify the crash window and explain why a local transaction cannot cover a remote provider?

## References and reviewed-on date

- [Android Room transactions](https://developer.android.com/reference/kotlin/androidx/room/package-summary) — local atomic operations.
- [Android offline-first data layer](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable source of truth concepts.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
