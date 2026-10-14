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

اكتب مجموعة اختبارات وحدة (Unit Tests) لمسار إعادة محاولة الدفع البنكي (Payment Retry Path) تضمن قطعياً عدم حدوث سحب مالي مزدوج (No Duplicate Charge)؟

1. متطلبات الاختبار الحتمية لمعاملات الدفع:
   - **الاختبار 1: التحقق من ثبات مفتاح الـ Idempotency**: التأكد من أن جميع محاولات إعادة الدفع لنفس الطلب ترسل نفس الـ UUID بالضبط دون توليد مفتاح جديد.
   - **الاختبار 2: معالجة الـ Timeout والمطابقة السيرفرية (Reconciliation)**: إذا حدث انقطاع في الشبكة أثناء أول طلب، يجب أن يستعلم الاختبار عن حالة المعاملة أولاً (`GET /status`)، وإذا وجد أن السيرفر قد خصم المبلغ بنجاح، يُمنع إرسال طلب خصم ثانٍ فوراً!
   - **الاختبار 3: حظر محاولات الخصم المتزامنة (Concurrency Lock)**: التأكد من أن الضغط السريع المتكرر على زر الدفع (Double-Tap) يُشغل معاملة واحدة فقط ويحظر الباقي.

2. كيفية الإثبات في كود الاختبار:
   - نستخدم MockWebServer أو Fake Payment API يسجل عدد طلبات الـ POST الصادرة؛ ونؤكد أن عدد طلبات الخصم الحقيقية لا يتجاوز 1 تحت أي ظرف.

## Practical walkthrough

كتابة اختبارات وحدة صارمة تضمن عدم تكرار سحب الأموال عند حدوث Timeout أو ضغطات متكررة:
```kotlin
class PaymentSafetyTest {
    @Test
    fun `network timeout triggers reconciliation and never executes duplicate charge`() = runTest {
        var chargeCallCount = 0
        var reconciliationCallCount = 0

        val fakePaymentApi = object : PaymentApiService {
            override suspend fun executeCharge(idempotencyKey: String, amount: Long): ChargeResponse {
                chargeCallCount++
                // محاكاة سحب حقيقي على السيرفر لكن انقطعت الاستجابة قبل وصولها للموبايل:
                throw SocketTimeoutException("Read timeout")
            }

            override suspend fun reconcileStatus(idempotencyKey: String): PaymentStatusResponse {
                reconciliationCallCount++
                // السيرفر يؤكد أن المعاملة تم خصمها بنجاح بالفعل:
                return PaymentStatusResponse(isAuthorized = true, transactionId = "tx_9988")
            }
        }

        val coordinator = PaymentCoordinator(fakePaymentApi, FakePaymentDao())
        val result = coordinator.payOrder(orderId = "order_1", amountCents = 5000)

        // 1. التأكد من نجاح العملية للمستخدم بناءً على الاستعلام السيرفري:
        assertTrue(result is PaymentResult.Success)
        assertEquals("tx_9988", (result as PaymentResult.Success).transactionId)

        // 2. البرهان الحاسم: طلب الخصم تم استدعاؤه مرة واحدة فقط ولم يتكرر إطلاقاً!
        assertEquals(1, chargeCallCount)
        assertEquals(1, reconciliationCallCount)
    }
}
```

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

Test payment safety by asserting that all retry attempts transmit the identical UUID idempotency key, verifying that socket timeouts trigger read-only reconciliation queries rather than blind charge replays, and strictly asserting that the payment gateway charge method was invoked exactly once.

## Interview answer — structured

Testing payment paths requires mathematical guarantees that duplicate charges are impossible under any failure permutation.

First, **Asserting Idempotency Key Stability**. Next, write a test verifying that when an order is created, an `idempotencyKey = UUID` is persisted locally. Assert that across multiple retry loops, crashes, and app restarts for that order ID, the captured HTTP `Idempotency-Key` header remains identical.
**Verifying Reconciliation Over Retry**. Simulate a network socket timeout on the initial charge request. Configure the test stub to throw `SocketTimeoutException` while recording that the backend processed the charge.
Assert that the client payment coordinator catches the timeout and invokes `reconcileStatus(idempotencyKey)` rather than invoking `executeCharge()` a second time. Assert that `executeCharge()` call count strictly equals 1, proving zero duplicate charges were attempted.
**Rapid Double-Tap Concurrency Protection**. Launch two concurrent payment requests for the same order simultaneously on two parallel coroutine jobs.
Finally, assert that an internal Mutex drops or rejects the second call, and that only one charge request hits the network.


## Interview answer — deep senior

From a financial compliance and test harness perspective, payment testing requires exhaustive state space exploration.

First, with Testing Database Transaction Rollbacks, test what happens if the local database crashes immediately before dispatching the network call. Assert that if inserting the local `PENDING` record fails, zero network calls execute, preventing untracked charges. Next, with Simulating Gateway 'Unknown' Statuses, if the reconciliation query itself times out, assert that the coordinator transitions state to `PENDING_MANUAL_VERIFICATION`. Assert that the UI renders a customer-support ticket reference and blocks the user from retrying the payment button until backend resolution confirms the order status.
Finally, with Idempotency Header Telemetry Assertions, assert via MockWebServer's `takeRequest()` that outgoing charge requests pass standard payment headers: `Idempotency-Key`, `X-Client-Timestamp`, and masked audit metadata.


## How to answer in the interview

- **Why:** timeout after commit creates duplicate-charge risk.
- **How:** persist one key, commit then lose reply, restart and retry same key.
- **Trade-off:** truthful Unknown UX versus unsafe instant success/failure.
- **Failure case:** a fake server is mistaken for production dedup proof.
- **Production solution:** backend concurrent same-key test and provider reconciliation.

## Deep-dive talking points

Prompt for after-commit fault, immutable parameters, concurrent server test, retention window and process death.

## Follow-up questions

- **Interviewer:** "What is the single most critical assertion in a payment retry unit test?"
  **Answer:** "Asserting that the charge mutation call count equals exactly 1 and was not re-invoked following a network timeout."

- **Interviewer:** "How do you test that double-clicking the payment button does not trigger parallel requests?"
  **Answer:** "Launch two concurrent payment coroutines simultaneously and assert that the payment API mock receives exactly one invocation."

## Self-check rubric

Inject a lost reply after server commit, restart the client and assert the same key and immutable amount are sent. Then test concurrent same-key requests against the backend and verify one charge; do not claim a fake server proves that guarantee.

## References and reviewed-on date

- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests) — provider-specific contract.
- [Android offline-first data layer](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable client state.

Technically reviewed against primary documentation on 2026-10-13.
