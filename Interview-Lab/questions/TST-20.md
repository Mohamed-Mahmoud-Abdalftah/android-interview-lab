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

## Concept and technical explanation

Testing payment retry workflows requires enforcing strict cryptographic idempotency guarantees to ensure that network timeouts or application restarts never trigger duplicate financial charges. When a client initiates a monetary transaction, the architecture must generate a unique, cryptographically stable Idempotency Key (such as a UUIDv4 combined with order identity) and persist the transaction locally to Room SQLite in an INITIALIZED state before dispatching the HTTP network request. If a lost-response failure occurs—where the server successfully processes the charge but the client experiences a read timeout or socket drop—the client retries the transaction using the exact same Idempotency Key. The remote payment gateway recognizes the duplicate submission and returns the original authorization result without re-billing the account. Tests must verify that the same key is transmitted across retries, that process resurrection resumes from local state, and that concurrent retry attempts are debounced.

## Practical walkthrough (English)

Testing idempotent payment retry and duplicate charge prevention:
```kotlin
// Payment service enforcing idempotency and local state persistence
class PaymentRepository(
    private val paymentApi: PaymentApi,
    private val paymentDao: PaymentDao
) {
    suspend fun processPayment(orderId: String, amount: Double): PaymentResult {
        // Retrieve existing transaction or create new one with persistent idempotency key
        val transaction = paymentDao.getTransaction(orderId) ?: PaymentEntity(
            orderId = orderId,
            idempotencyKey = UUID.randomUUID().toString(),
            amount = amount,
            status = PaymentStatus.PENDING
        ).also { paymentDao.insert(it) }

        return try {
            val response = paymentApi.charge(
                idempotencyKey = transaction.idempotencyKey,
                request = ChargeRequest(orderId, amount)
            )
            paymentDao.updateStatus(orderId, PaymentStatus.SUCCESS)
            PaymentResult.Success(response.chargeId)
        } catch (e: IOException) {
            // Network dropped or timed out; transaction remains PENDING for safe retry
            PaymentResult.RetryableError("Network timeout. Safe to retry.")
        }
    }
}

// Unit tests validating idempotency key reuse on network failure
class PaymentRepositoryTest {
    private val paymentApi = mockk<PaymentApi>()
    private val paymentDao = FakePaymentDao()
    private val repository = PaymentRepository(paymentApi, paymentDao)

    @Test
    fun processPayment_lostResponseTimeout_retriesWithExactSameIdempotencyKey() = runTest {
        val capturedKeys = mutableListOf<String>()

        // First attempt throws SocketTimeoutException simulating lost response
        coEvery {
            paymentApi.charge(capture(capturedKeys), any())
        } throws SocketTimeoutException("Read timed out") andThen ChargeResponse(chargeId = "ch_9876")

        // First call fails due to timeout
        val firstResult = repository.processPayment(orderId = "order_101", amount = 99.0)
        assertTrue(firstResult is PaymentResult.RetryableError)

        // Retry the payment for the same order
        val retryResult = repository.processPayment(orderId = "order_101", amount = 99.0)
        assertTrue(retryResult is PaymentResult.Success)

        // Assert that both network attempts used the exact same idempotency key
        assertEquals(2, capturedKeys.size)
        assertEquals(capturedKeys[0], capturedKeys[1])

        // Verify database records single transaction in SUCCESS state
        assertEquals(PaymentStatus.SUCCESS, paymentDao.getTransaction("order_101")?.status)
    }

    @Test
    fun processPayment_distinctOrders_generateDifferentIdempotencyKeys() = runTest {
        val capturedKeys = mutableListOf<String>()
        coEvery { paymentApi.charge(capture(capturedKeys), any()) } returns ChargeResponse("ch_1")

        repository.processPayment("order_A", 10.0)
        repository.processPayment("order_B", 20.0)

        // Assert distinct idempotency keys per order
        assertNotEquals(capturedKeys[0], capturedKeys[1])
    }
}
```

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

We test payment retries by simulating lost network responses and asserting strict idempotency key stability. The client persists an idempotency key into Room before calling the API. When a read timeout occurs after the server processed the charge, the retry logic uses the persisted key. The test captures outgoing HTTP headers to assert that both initial and retry attempts transmit the identical idempotency key, guaranteeing the server never debits the customer twice.

## Interview answer — structured

Testing payment workflows demands extreme rigor because a failure in retry logic can cause catastrophic duplicate billing of customers.
In distributed systems, the most dangerous failure mode is the lost-response scenario.
In this case, the payment gateway successfully debits the customer card, but the returning HTTP 200 response is severed by cellular packet loss or a client read timeout.
To guarantee that retrying does not create a second charge, the client must implement idempotent retries.
Before dispatching any network request, the repository creates a unique Idempotency Key and commits it to a local Room SQLite database alongside the order identifier in a pending status.
If the request fails with a network exception, the transaction record remains in the database.
When the user or a background worker retries the transaction, the repository reloads the existing record and submits the identical idempotency key in the HTTP header.
The remote payment gateway detects the key, matches it against its authorization ledger, and returns the original transaction receipt without charging the card again.
Our unit tests verify this contract by capturing all outgoing charge requests, asserting that retry calls reuse the exact same idempotency key, and verifying that the local database transitions to success without duplicate entries.

## Interview answer — deep senior

Under the hood, payment safety depends on a coordinated distributed consensus contract between the mobile client's SQLite database and the backend payment gateway.
The core vulnerability during payment processing is non-atomic failure across process boundaries.
If an application generates an idempotency key purely in memory, an Android process death or app crash during a network timeout would cause the resurrection process to generate a new key on retry, triggering a double charge.
Senior engineers mandate an offline-first transactional sequence: the client begins a SQLite database transaction, writes the order ID and generated UUID idempotency key to disk with write-ahead logging (WAL), and commits before opening the network socket.
When MockWebServer simulates an HTTP 504 Gateway Timeout or a TCP socket drop via SocketPolicy.DISCONNECT_DURING_RESPONSE_BODY, OkHttp throws a SocketTimeoutException.
The test asserts that the repository catches this transport exception without clearing the local idempotency key.
During the subsequent retry invocation, the repository queries the database, extracts the stored key, and transmits it via the Idempotency-Key HTTP header.
On the backend, payment systems (such as Stripe or custom banking APIs) lock the idempotency key in Redis with a 24-hour TTL; if a second request arrives with that key, the gateway short-circuits execution and echoes the cached charge response.
Tests also verify process resurrection by simulating an app kill between the network drop and the retry, proving the system is resilient against sudden mobile process death.

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
