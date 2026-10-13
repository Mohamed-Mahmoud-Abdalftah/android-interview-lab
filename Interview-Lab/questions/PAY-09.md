---
id: "PAY-09"
question: "How do you isolate a hardware/EMV SDK behind a clean interface?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "B"
phase: 5
priority: "P2"
order: 479
editorial_status: "reviewed"
---

# PAY-09

## Original interview question

How do you isolate a hardware/EMV SDK behind a clean interface?

## What the interviewer evaluates

- SDK adapter boundary and domain-owned state.
- Callback races, device disconnect and test fakes.

## Explanation in Arabic

Hardware/EMV SDK يتغير حسب vendor والجهاز، فلا نخلي UI أو ViewModel يفهم raw callbacks وerror codes. نعمل interface صغير لعمليات `start/cancel/status` ونتائج domain واضحة، وadapter يترجم SDK events ويربطها بـoperation ID. لكن interface ما يلغي شروط certification ولا يخلي callback دليل نهائي على issuer outcome.

## Practical walkthrough

خلي UI تقول `authorize(intent)` وتستقبل domain outcome، والـadapter وحده يعرف أسماء callbacks وerror codes بتاعة vendor. لو SDK رجّعت transport error، map إلى `Unknown` مش `Declined` من غير دليل. اعمل fake adapter لاختبار race وlate callbacks، واختبر adapter الحقيقي على hardware المعتمد لأن abstraction مش بديل certification.

## Why it matters and how it works

A domain port owns stable operation identity and an explicit outcome type including Unknown. The vendor adapter handles threading, lifecycle, callback ordering and error mapping. The repository persists attempt state before invoking the SDK and reconciles against backend/provider authority after ambiguous events.

## Worked example

Conceptual Kotlin contract: `interface TerminalGateway { suspend fun authorize(id: String, amountMinor: Long): TerminalOutcome; suspend fun status(id: String): TerminalOutcome }` where `TerminalOutcome` includes Approved, Declined and Unknown. The adapter wraps vendor callbacks with cancellation and timeout rules; this signature alone is not a complete EMV implementation.

### Kotlin/Android sketch

```kotlin
sealed interface TerminalOutcome {
    data class Approved(val providerRef: String) : TerminalOutcome
    data class Declined(val code: String) : TerminalOutcome
    data object Unknown : TerminalOutcome
}
interface TerminalGateway {
    suspend fun authorize(operationId: String, amountMinor: Long): TerminalOutcome
    suspend fun status(operationId: String): TerminalOutcome
}
// Vendor adapter implements this port; Unknown covers ambiguous transport loss.
// Cancellation of a callback wait must not be interpreted as issuer decline.
```

## Trade-offs and decision criteria

Abstraction improves testing and vendor replacement but can hide provider-specific capabilities if too generic. Keep a capability model or provider-specific extension for certified functions rather than forcing all SDKs into false equivalence.

## Failure modes

A callback arrives twice or after the UI screen closes. If UI owns it, it may duplicate a charge or lose an approval. Adapter correlates callback ID, repository commits guarded transitions, and backend reconciles unknown results.

## Production perspective

Run contract tests against fake adapter plus hardware test matrix by model, ABI and SDK version. Preserve raw vendor references only in restricted audit storage, never card data in logs. Certification constraints are documented.

## Interview answer — short

“I put an explicit payment port between the domain and vendor SDK. The adapter owns callback translation, threading, and cancellation, while the domain keeps operation identity and treats ambiguous transport outcomes as Unknown.”

## Interview answer — structured

“The UI should request a payment intent, not call vendor callbacks directly. A TerminalGateway adapter translates SDK methods, threading and error codes into approved, declined or unknown domain outcomes tied to a stable operation ID. A repository persists state and handles process death; backend/provider reconciliation settles ambiguous results. I test the interface with a fake and still run real hardware/certification tests for SDK-specific behavior. The adapter translates a vendor disconnect into Unknown unless the provider proves a decline.”

## Interview answer — deep senior

“I draw the boundary around what the application controls: intent identity, state persistence, cancellation semantics and observability. The adapter may wrap callbacks into a suspend API, but cancellation of a coroutine does not imply an in-flight EMV authorization was canceled. I map each SDK event to a state transition with original references, handle duplicate/late callbacks and device disconnection, and expose Unknown when evidence is insufficient. The abstraction stays honest about provider-specific void/reversal capabilities. Contract tests validate mapping; hardware matrices cover firmware, ABI and release builds. Certification constraints are documented. I keep certification and hardware matrix work explicit; a clean Kotlin interface alone does not validate EMV behavior. I would keep the domain port small: authorize, cancel if supported, and status, with explicit Approved, Declined, and Unknown outcomes carrying only safe references. The adapter handles vendor callbacks, timeout, threading, and any JNI or device lifecycle details. It maps vendor codes through a reviewed table and never treats a disconnect as an issuer decline without evidence. The repository commits an attempt before invoking the port and owns reconciliation. A fake adapter makes deterministic race tests possible, while a hardware test matrix checks firmware-specific callback order and device disconnects. The interface is an engineering seam, not proof that the implementation meets EMV certification or acquirer rules.”

## How to answer in the interview

- **Why:** SDK callbacks and threading should not leak into checkout logic.
- **How:** define a small port with explicit Unknown and adapt vendor events behind it.
- **Trade-off:** abstraction cannot erase hardware or certification rules.
- **Failure case:** mapping disconnect to decline or losing the original reference.
- **Production solution:** contract tests, real-device validation, and versioned error mapping.

## Deep-dive talking points

Prompt for narrow port, cancellation versus payment cancellation, duplicate callbacks, capability differences and hardware tests.

## Follow-up questions

- [PAY-11](../pay-11/): How test timeout/disconnect? **Answer:** fake callback schedules plus real device drills.
- [PAY-12](../pay-12/): What survives power loss? **Answer:** durable operation identity and backend record.

## Self-check rubric

Can I design an SDK port without erasing provider-specific constraints or conflating coroutine cancellation with payment cancellation?

## References and reviewed-on date

- [Android app architecture data layer](https://developer.android.com/topic/architecture/data-layer) — repository/data-source boundaries.
- [Kotlin cancellation](https://kotlinlang.org/docs/cancellation-and-timeouts.html) — cooperative cancellation.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
