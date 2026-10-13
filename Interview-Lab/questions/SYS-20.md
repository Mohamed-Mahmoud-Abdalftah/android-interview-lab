---
id: "SYS-20"
question: "A payment was authorized but the UI timed out. Design recovery and reconciliation."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "C"
phase: 4
priority: "P1"
order: 349
editorial_status: "reviewed"
---

# SYS-20

## Original interview question

A payment was authorized but the UI timed out. Design recovery and reconciliation.

## What the interviewer evaluates

Recover an authorized payment after UI timeout by querying ledger and preserving Pending.

## Explanation in Arabic

UI timeout بعد authorization معناها العميل مش عارف النتيجة؛ backend ممكن يكون Authorized بالفعل. نخزن operation ID وidempotency key قبل submit، ونخلي UI Pending/Unknown، ثم نسأل status endpoint أو نستنى server event موثوق. ما نعملش authorization جديدة بمفتاح جديد، ولا نعمل capture/reversal من التخمين. backend state machine يحدد authorized, captured, expired أو reversed.

## Practical walkthrough

الـbackend عمل authorize لكن شاشة POS استنت deadline؛ ده Unknown للعميل، رغم إن السيرفر عارف Authorized. احفظ operation ID قبل الإرسال وخلي UI Pending، واسأل status endpoint أو ledger عند العودة. نفس idempotency key فقط ضمن عقد provider، ولا تعمل capture أو reversal من التخمين. لو app اتقتلت، WorkManager تتابع reconciliation؛ support تشوف timeline من غير card secrets.

## Why it matters and how it works

Authorization may expire or require later capture; status lookup and reconciliation must distinguish those states. A worker can resume after process death, using the same key for safe retry only under server contract. UI should disable duplicate submit and provide support correlation ID. Metrics track unresolved Unknown age.

## Worked example

Conceptual Kotlin recovery API; exact states belong to the payment backend contract.

```kotlin
interface PaymentGateway {
    suspend fun status(operationId: String): PaymentStatus
}
suspend fun resolveAfterTimeout(id: String, gateway: PaymentGateway): PaymentStatus =
    gateway.status(id)
// If status is temporarily unknown, retain Pending and retry reconciliation.
```

## Trade-offs and decision criteria

Pending UX can be frustrating but avoids false decline/duplicate charge. Status endpoints and durable workers add backend/client complexity. Automatic reversal may be appropriate only after backend-confirmed state and business policy, not merely UI timeout.

## Failure modes

A UI that shows Failed on timeout may invite the user to pay again and duplicate authorization. A cancellation exception cannot roll back an already accepted server operation. A stale cached status can miss a later capture; use authoritative version/receipt.

## Production perspective

A ticket app records one checkout ID, submits authorization, shows Pending after timeout and reconciles in WorkManager. Backend exposes ledger status and controls capture. Support can search correlation ID; tests lose the response after server acceptance.

## Interview answer — short

“I treat UI timeout as unknown server outcome. I keep the original payment ID and Pending state, query authoritative status, and never create a new authorization key until the backend contract proves it safe.”

## Interview answer — structured

“The client stopped waiting, but the server may have authorized. I persist an operation ID and idempotency key before send, disable duplicate submit and show Pending rather than Failed. A status endpoint or backend event resolves Authorized, Declined, Captured or another explicit state. WorkManager resumes this reconciliation after process death. I only retry with the same key under documented server semantics, and I do not reverse or capture based solely on the UI timeout.”

## Interview answer — deep senior

“I walk the commit window: the backend accepts authorization, response is lost, app may die, and a new UI appears. Durable local operation state and server ledger query let us converge. Idempotency protects logical retries if the server enforces key retention and payload matching; it does not mean one HTTP packet. Authorization and capture are distinct transitions, so the UI must display the exact authoritative state and avoid promising settlement early. Reversal is a separate linked operation after policy checks. I monitor Pending age, alert support on unresolved cases and test delayed status propagation, duplicate taps, process restart and a response lost after commit. Metrics track unresolved Unknown age. I would maintain a durable local row keyed by the original operation ID so process death cannot erase the ambiguity. On relaunch a worker queries the backend's ledger or provider status; it never sends a fresh authorization merely because the screen timed out. The UI says Pending and later reflects Authorized, Settled or Reversed only from authoritative evidence. I would test the response-loss window, repeated worker execution and delayed provider callbacks. Support tools should show a safe audit timeline tied to the same ID.”

## How to answer in the interview

- **Why:** a lost response does not undo authorization.
- **How:** persist identity, show Pending, and converge on authoritative status.
- **Trade-off:** waiting UX and support tooling are more complex.
- **Failure case:** second authorize with a new key duplicates effect.
- **Production solution:** ledger query, idempotency contract, durable recovery, and audit timeline.

## Deep-dive talking points

Trace authorization versus capture and show why timeout is not failure.

## Follow-up questions

- [SYS-05](../sys-05/): What is payment lifecycle? **Answer:** explicit server-authoritative states and linked operations.
- [DAT-20](../dat-20/): How recover lost response? **Answer:** query status by original operation ID.

## Self-check rubric

Can I preserve original key, represent Unknown and reconcile authorization/capture separately?

## References and reviewed-on date

- [Kotlin withTimeout API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout.html) — timeout semantics.
- [Android task scheduling](https://developer.android.com/develop/background-work/background-tasks/persistent) — restartable reconciliation.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-13; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
