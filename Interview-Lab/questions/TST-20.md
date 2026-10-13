---
id: "TST-20"
question: "Write tests for a payment retry path guaranteeing no duplicate charge."
topic: "Testing, Quality & Reliability"
code: "TST"
group: "C"
phase: 4
priority: "P1"
order: 415
editorial_status: "reviewed"
---

# TST-20

## Original interview question

Write tests for a payment retry path guaranteeing no duplicate charge.

## What the interviewer evaluates

- Lost-response test and distinction between local retry behavior and real server guarantee.
- Stable idempotency identity, process death and reconciliation.

## Explanation in Arabic

جملة “no duplicate charge” لا تثبتها unit test على العميل وحده. أخطر sequence إن backend سجّل approval لكن response ضاع؛ العميل يرى timeout، يخزن Unknown ولا يولّد `UUID` جديدة. test العميل تبدأ بـintent محفوظة فيها key وamount ثابتين، fake server يعمل commit ثم يقطع الرد، وبعد restart تعمل retry أو status lookup وتؤكد نفس key/parameters.

## Practical walkthrough

لكن fake فيها dedup متوقع لا تثبت production؛ backend integration test تبعت طلبين بنفس key بالتوازي وتتأكد من charge record واحدة، وترفض نفس key بمبلغ مختلف. provider sandbox يختبر retention/status contract الخاص به. لو key انتهت صلاحيتها أو status ما اتحسمتش، يلزم reconciliation/operations escalation بدل charge عمياء. اختبر duplicate taps، crash بعد persist، وlog redaction.

## Why it matters and how it works

Idempotency protects one intended business effect across repeated deliveries; it does not make network execution exactly once. The server must bind key to immutable parameters and decide concurrent requests atomically. The client persists the identity before the first send.

## Worked example

The dangerous sequence is approval followed by a lost response. This JUnit 5 model uses an in-memory durable-store stand-in and a fake server that commits before dropping its first reply. The fake's deduplication is a test fixture, **not proof that the production backend or provider deduplicates**.

```kotlin
import java.io.IOException
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class PaymentRetryTest {
    data class Request(val key: String, val amountMinor: Long)
    class Store(var pending: Request? = null) // Replace with durable storage in the app.

    class FakeServer {
        val received = mutableListOf<Request>()
        val charges = mutableMapOf<String, Long>()
        var dropFirstReply = true

        fun charge(request: Request): Boolean {
            received += request
            val previous = charges[request.key]
            require(previous == null || previous == request.amountMinor)
            charges.putIfAbsent(request.key, request.amountMinor)
            if (dropFirstReply) {
                dropFirstReply = false
                throw IOException("reply lost after commit")
            }
            return true
        }
    }

    class Client(private val store: Store, private val server: FakeServer) {
        fun start(request: Request): Boolean {
            store.pending = request // Persist before the first network send.
            return server.charge(request)
        }
        fun retry(): Boolean = server.charge(requireNotNull(store.pending))
    }

    @Test fun retryAfterLostReplyKeepsOneIdentity() {
        val store = Store()
        val server = FakeServer()
        val intent = Request("P1", 2_500)
        assertThrows(IOException::class.java) { Client(store, server).start(intent) }

        val restartedClient = Client(store, server)
        assertTrue(restartedClient.retry())
        assertEquals(listOf(intent, intent), server.received)
        assertEquals(mapOf("P1" to 2_500L), server.charges)
        assertThrows(IllegalArgumentException::class.java) {
            server.charge(Request("P1", 3_000))
        }
    }
}
```

In the real client, persist the request atomically before sending, surface an Unknown state on the first timeout, and reconcile by status lookup or same-key retry under the provider's documented contract. Run two concurrent P1 requests against a backend integration environment and assert one charge record; the local fake cannot establish that cross-process guarantee.

## Trade-offs and decision criteria

Local test is fast but only checks emitted requests. Provider sandbox may differ from production retention/race behavior; document its contract and perform reconciliation tests. Conservative Unknown UI adds friction but avoids blind double charge.

## Failure modes

A mock returns timeout without recording a server effect, so test falsely assumes no charge. Explicitly place the fault after remote commit. Changed amount under same key must be rejected, not treated as a new operation.

## Production perspective

CI has unit/client HTTP tests, backend concurrency/idempotency tests, and provider sandbox reconciliation. Alerts watch duplicate IDs and unresolved unknowns without card data.

## Interview answer — short

“I simulate approval followed by lost response, then retry with the same durable operation ID and verify server-side deduplication. A client test alone cannot guarantee no duplicate charge.”

## Interview answer — structured

“I first persist an immutable payment intent and idempotency key. The test server commits one charge, then drops the reply so the client sees timeout. The client must show Unknown, reuse the key on retry or query status, and survive process death. A separate backend integration test sends concurrent same-key requests and proves only one business effect; changed parameters are rejected. Provider-specific retention and reconciliation remain part of the release plan.”

## Interview answer — deep senior

“I split the guarantee across trust boundaries. The client test proves it persists one immutable payment intent before sending, keeps the same idempotency key and amount after a timeout or process restart, and shows Unknown instead of Declined when the reply is ambiguous. My HTTP test records the actual header and body and injects the failure after the fake server commits; dropping the response before the send would miss the dangerous case. A local fake can model deduplication, but it cannot prove the production ledger. I run a backend concurrency test with two same-key requests and assert one business effect, and another test that rejects changed parameters under the same key. A provider sandbox test checks its documented retention, status lookup and reconciliation behavior. I also test duplicate taps, a crash between durable intent creation and send, and retry after an unresolved status. If the key expires or the authority cannot be reached, the UI must remain pending or unknown with a support reference and operational reconciliation; a new key is not a safe default. I never promise exactly-once network delivery—only duplicate-safe effects under an explicit server and provider contract.”

## How to answer in the interview

- **Why:** timeout after commit creates duplicate-charge risk.
- **How:** persist one key, commit then lose reply, restart and retry same key.
- **Trade-off:** truthful Unknown UX versus unsafe instant success/failure.
- **Failure case:** a fake server is mistaken for production dedup proof.
- **Production solution:** backend concurrent same-key test and provider reconciliation.

## Deep-dive talking points

Prompt for after-commit fault, immutable parameters, concurrent server test, retention window and process death.

## Follow-up questions

- [PAY-02](../pay-02/): What does idempotency guarantee? **Answer:** one business effect under a server contract, not one HTTP execution.
- [PAY-08](../pay-08/): What does UI show? **Answer:** Unknown/pending until authority resolves status.

## Self-check rubric

Inject a lost reply after server commit, restart the client and assert the same key and immutable amount are sent. Then test concurrent same-key requests against the backend and verify one charge; do not claim a fake server proves that guarantee.

## References and reviewed-on date

- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests) — provider-specific contract.
- [Android offline-first data layer](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable client state.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
