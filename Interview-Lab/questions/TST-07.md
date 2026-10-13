---
id: "TST-07"
question: "What is the test pyramid, and where do contract tests fit?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "A"
phase: 4
priority: "P1"
order: 402
editorial_status: "reviewed"
---

# TST-07

## Original interview question

What is the test pyramid, and where do contract tests fit?

## What the interviewer evaluates

- Understanding the Test Pyramid as an economic and diagnostic distribution model (Unit, Integration, Contract, End-to-End).
- Role and definition of Consumer-Driven Contract (CDC) testing between Android clients and backend microservices.
- Concrete test implementation using MockWebServer, schema validation, and error contract assertions.
- Safe serialization contracts: handling unexpected fields, nullability drifts, and unknown enum values without app crashes.
- Practical balance between lightning-fast contract verification in CI and complete UI/instrumentation E2E journeys.

## Explanation in Arabic

هرم الاختبارات (Test Pyramid) هو نموذج اقتصادي لتوزيع الاختبارات بناءً على السرعة وتكلفة الصيانة ومستوى الثقة. في قاعدة الهرم بيكون عندنا عدد كبير جدًا من الـUnit Tests السريعة اللي بتفحص منطق البيزنس في أجزاء من الثانية. في المنتصف بتيجي الـIntegration Tests والـContract Tests. الـContract Tests بتمثل اتفاق رسمي وموثق بين الـConsumer (تطبيق الأندرويد) والـProvider (الـBackend API). التطبيق بيحدد العقد اللي متوقعه: شكل الـJSON، الحقول الإلزامية، الـHTTP headers (زي `Idempotency-Key`)، وحالات الـError. الـContract Test بتتحقق إن الـclient parser بيتعامل مع الـcontract ده بأمان، وبنفس الوقت الـcontract بيصدر كـPact أو JSON schema يتشغل في الـCI بتاع الـbackend عشان نضمن إن أي تعديل من مهندسي الـbackend مش هيكسر التطبيق في الإنتاج.

## Practical walkthrough

لو الـbackend غير اسم حقل من `payment_id` لـ `transaction_id`، كل الـUnit Tests عند الفريقين ممكن تنجح لو كانت بتستخدم mocks يدوية! والـUI E2E test بطيئة ومكلفة وممكن تفشل لأسباب شبكة مش واضحة. الـContract Test بتملأ الفجوة دي فورًا: بنعمل MockWebServer test بيستقبل الـJSON الحقيقي المتفق عليه ويثبت إن الـclient بيقراه صح، وبنختبر كمان حالات الـEdge: لو الـbackend بعت enum جديد مش معروف للـclient (مثال: status غير متوقعة)، هل التطبيق هيقفل بـ `SerializationException` ولا الـparser هيرجع `PaymentStatus.UNKNOWN` بأمان؟ كده بنكتشف كسر الـAPI في ثوانٍ معدودة داخل الـPR قبل ما أي كود يوصل لنسخة الـRelease.

## Why it matters and how it works

The classic testing pyramid balances execution cost against diagnostic value across four tiers:
1. **Unit Tests (Base, ~70%):** Fast, deterministic JVM tests exercising pure domain policies, ViewModels, and algorithms with zero network or platform dependencies.
2. **Integration Tests (~20%):** Validates real boundaries within the app—such as Room SQL queries running against an in-memory SQLite database, or serialization converters parsing JSON strings.
3. **Contract Tests (Boundary Layer):** Focuses specifically on the interface agreement between consumer and provider. They verify request payloads, authentication headers, response schemas, error codes, and field nullability without spinning up a live backend environment.
4. **End-to-End / UI Tests (Apex, ~10%):** Slow, high-cost journeys (using Maestro, Espresso, or Playwright) validating end-to-end wiring, OS permissions, and user journeys on real emulators or devices.

Contract tests can be executed locally on the client using `MockWebServer` with verified JSON fixtures, or through formalized consumer-driven contract tools like Pact, where consumer expectations generate contract artifacts that the backend CI pipeline tests against real endpoints.

## Worked example

Here is an executable Kotlin contract test demonstrating contract validation for a financial payments API using OkHttp `MockWebServer`:

```kotlin
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import okhttp3.OkHttpClient
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import retrofit2.Retrofit
import retrofit2.converter.kotlinx.serialization.asConverterFactory
import okhttp3.MediaType.Companion.toMediaType
import retrofit2.http.Body
import retrofit2.http.Header
import retrofit2.http.POST
import java.util.UUID

// ==========================================
// 1. CONTRACT MODELS (Resilient Serialization)
// ==========================================

@Serializable
enum class PaymentIntentStatus {
    @SerialName("REQUIRES_PAYMENT_METHOD") REQUIRES_PAYMENT_METHOD,
    @SerialName("REQUIRES_ACTION") REQUIRES_ACTION,
    @SerialName("SUCCEEDED") SUCCEEDED,
    @SerialName("FAILED") FAILED,
    UNKNOWN // Fallback for backward compatibility when backend adds new statuses
}

@Serializable
data class CreatePaymentIntentRequest(
    @SerialName("amount_cents") val amountCents: Long,
    @SerialName("currency") val currency: String,
    @SerialName("payment_method") val paymentMethod: String
)

@Serializable
data class PaymentIntentResponse(
    @SerialName("intent_id") val intentId: String,
    @SerialName("status") val status: PaymentIntentStatus = PaymentIntentStatus.UNKNOWN,
    @SerialName("next_action_url") val nextActionUrl: String? = null
)

interface PaymentContractApi {
    @POST("v1/payment/intents")
    suspend fun createPaymentIntent(
        @Header("Idempotency-Key") idempotencyKey: String,
        @Body request: CreatePaymentIntentRequest
    ): PaymentIntentResponse
}

// ==========================================
// 2. EXECUTABLE CONTRACT TEST
// ==========================================

class PaymentContractTest {
    private val server = MockWebServer()
    private val json = Json {
        ignoreUnknownKeys = true // Crucial contract rule: tolerate additional backend fields
        coerceInputValues = true // Map unrecognized values safely
    }

    private val api: PaymentContractApi

    init {
        server.start()
        val retrofit = Retrofit.Builder()
            .baseUrl(server.url("/"))
            .client(OkHttpClient.Builder().build())
            .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
            .build()
        api = retrofit.create(PaymentContractApi::class.java)
    }

    fun tearDown() {
        server.shutdown()
    }

    fun testPaymentIntentSuccessContract() = kotlinx.coroutines.runBlocking {
        // Agreed contract response fixture
        val contractResponseJson = """
            {
              "intent_id": "pi_9876543210",
              "status": "REQUIRES_ACTION",
              "next_action_url": "https://pay.bank.com/3ds/verify",
              "server_internal_trace": "trace_xyz" 
            }
        """.trimIndent()

        server.enqueue(
            MockResponse()
                .setResponseCode(200)
                .setHeader("Content-Type", "application/json")
                .setBody(contractResponseJson)
        )

        val idempotencyKey = UUID.randomUUID().toString()
        val response = api.createPaymentIntent(
            idempotencyKey = idempotencyKey,
            request = CreatePaymentIntentRequest(
                amountCents = 15000,
                currency = "EGP",
                paymentMethod = "CARD"
            )
        )

        // 1. Assert Outgoing Request Contract
        val recordedRequest = server.takeRequest()
        check(recordedRequest.method == "POST")
        check(recordedRequest.path == "/v1/payment/intents")
        check(recordedRequest.getHeader("Idempotency-Key") == idempotencyKey)
        check(recordedRequest.body.readUtf8().contains("\"amount_cents\":15000"))

        // 2. Assert Incoming Response Contract
        check(response.intentId == "pi_9876543210")
        check(response.status == PaymentIntentStatus.REQUIRES_ACTION)
        check(response.nextActionUrl == "https://pay.bank.com/3ds/verify")
        // Unknown field 'server_internal_trace' was ignored without throwing exception!
    }

    fun testBackendDriftWithNewStatusDoesNotCrashClient() = kotlinx.coroutines.runBlocking {
        // Backend introduces a new status 'PENDING_MANUAL_REVIEW' before Android app updates
        val driftedJson = """
            {
              "intent_id": "pi_111",
              "status": "PENDING_MANUAL_REVIEW"
            }
        """.trimIndent()

        server.enqueue(MockResponse().setResponseCode(200).setBody(driftedJson))

        val response = api.createPaymentIntent(
            idempotencyKey = "key_1",
            request = CreatePaymentIntentRequest(500, "EGP", "WALLET")
        )

        // Verifies fallback contract: gracefully falls back to UNKNOWN rather than crashing
        check(response.status == PaymentIntentStatus.UNKNOWN)
    }
}
```

## Trade-offs and decision criteria

1. **Contract Tests vs Mocking Everything in Unit Tests:**
   - Unit tests that rely on handwritten mocks (e.g. `whenever(api.create(...)).thenReturn(...)`) will continue passing with 100% green builds even after the backend completely changes field names or nullability.
   - Contract tests exercise the actual HTTP serialization layer and JSON parser, verifying that real serialized strings map correctly to domain models.

2. **Contract Tests vs Full E2E UI Tests:**
   - Full E2E UI tests across real staging environments are notoriously flaky, slow (minutes per test), and dependent on network availability and test account credentials.
   - Contract tests execute in milliseconds on the JVM, giving immediate, localized feedback on breaking API changes. However, contract tests cannot verify actual backend infrastructure routing, database replication, or OAuth token refresh lifetimes.

3. **Tooling Selection:**
   - **MockWebServer with Shared JSON Fixtures:** Lightweight, simple to integrate into standard Gradle test tasks, requiring no external broker.
   - **Pact (Consumer-Driven Contracts):** Generates formal `.pact` contract files that are published to a Pact Broker, enabling backend CI builds to automatically verify and prevent breaking deployment when client contracts fail (`can-i-deploy` verification).

## Failure modes

- **Fragile Serialization with Strict Unknown Keys:** Configuring JSON parsers without `ignoreUnknownKeys = true`. When the backend adds an optional telemetry field, every older version of the Android app crashes upon opening.
- **Strict Enum Deserialization Without Fallbacks:** If the backend adds a new enum value (e.g. `PAYMENT_PENDING_AML`), an Android client without an `UNKNOWN` fallback throws `SerializationException`, taking down the entire checkout screen.
- **Verifying Only HTTP 200 Happy Path:** Forgetting to test error contract shapes (HTTP 400 Bad Request, 409 Conflict, 422 Unprocessable Entity). A client that expects `{ "message": "..." }` will crash if the server returns `{ "errors": [{ "code": "..." }] }`.
- **Assuming Contract Tests Replace E2E Testing:** A contract test passes because the schema matches, but the production API Gateway rejects requests due to a mismatched CORS header or expired TLS cipher suite. A small suite of real smoke E2E tests remains essential.

## Production perspective

In a production mobile release pipeline:
- Run contract tests on every pull request as part of the fast JVM unit test suite.
- Store contract JSON fixtures in a version-controlled directory or export Pact files during test runs.
- Integrate contract verification in backend CI: when backend engineers submit a PR modifying an API response, the CI pipeline runs the Android consumer pacts; if a required field is removed or modified, the backend build fails automatically before deployment.
- Maintain a small set (5–10) of critical end-to-end smoke tests (e.g., login, payment checkout) executed nightly or pre-release against a staging sandbox environment.

## Interview answer — short

“The test pyramid prioritizes many fast, low-cost unit tests at the base, fewer integration and contract tests in the middle, and a minimal set of expensive E2E tests at the apex. Contract tests sit between unit and E2E tests, verifying that the Android client and backend API agree on request formats, headers, and response schemas using tools like MockWebServer or Pact, preventing API drift without slow E2E suites.”

## Interview answer — structured

“When evaluating the test pyramid and contract testing:
1. **Pyramid Economics:**
   - **Unit Tests (~70%):** Fast, isolated tests for ViewModels, Use Cases, and domain calculations.
   - **Integration Tests (~20%):** Validates Room queries, database migrations, and repository cache logic.
   - **Contract Tests:** Sits at the network boundary, ensuring consumer expectations match provider responses.
   - **E2E Tests (~10%):** UI tests for critical checkout or authentication journeys on emulators.
2. **Why Hand-Crafted Mocks Fail:** Unit tests with mock responses pass even when the backend renames JSON fields. Contract tests run actual JSON serialization through OkHttp and Kotlinx Serialization.
3. **Consumer-Driven Contract (CDC):** Android defines the contract fixture (required fields, headers, and error shapes). In CI, tools like Pact verify that the backend implements these expectations before deploying.
4. **Resilient Deserialization:** Contract tests enforce resilience—such as tolerating unknown keys and mapping new server enum variants to `UNKNOWN` safely.
5. **Production Balance:** Fast contract tests catch schema drift on PRs, while a small set of automated E2E tests verify deployed routing and authentication.”

## Interview answer — deep senior

“A senior engineer views the test pyramid not as a dogmatic percentage rule, but as a risk-based economics model. The higher you climb the pyramid, the slower, more expensive, and more brittle the tests become.

In modern microservice architectures, the most common production outage is API contract drift: the backend modifies an endpoint or field nullability, while the mobile team discovers it only after release because unit tests were insulated behind green stubs. Conversely, relying on end-to-end UI tests to catch schema drift is disastrous—they are slow, flakily fail on network blips, and pinpoint failures poorly.

Contract tests solve this exact boundary risk. In my architecture, I implement consumer contract tests using MockWebServer and Kotlinx Serialization. The test validates both sides of the HTTP exchange:
1. **Request Contract:** Asserts exact HTTP verbs, paths, required headers (such as `Idempotency-Key` or `X-Client-Version`), and serialized JSON request body formats.
2. **Response Contract & Resilience:** Tests that agreed JSON payloads deserialize into domain models, and explicitly tests negative scenarios. I verify that unknown keys are safely ignored (`ignoreUnknownKeys = true`), nullable fields are accommodated, and unrecognized enum values gracefully fall back to `UNKNOWN` instead of throwing a fatal `SerializationException`.

Furthermore, in enterprise systems, we advance this to Consumer-Driven Contract testing via Pact. The Android test suite generates a contract artifact specifying the exact subset of the API our screens consume. This contract is uploaded to a Pact Broker, and the backend CI pipeline runs against it on every commit. If a backend engineer removes a field that our app relies on, their CI pipeline breaks immediately (`can-i-deploy: false`).

Contract tests don't eliminate E2E tests entirely; they relieve E2E tests from verifying schema mechanics. We reserve E2E tests for verifying deployed infrastructure, TLS handshake, gateway authentication tokens, and critical revenue journeys.”

## How to answer in the interview

- **Why:** Pure unit mocks miss API drift; E2E tests are too slow and flaky to catch JSON schema mismatches efficiently.
- **How:** Pyramid balances unit (policy), integration (persistence), contract (API interface), and E2E (user journeys). Contract tests use MockWebServer/Pact with real serialization and schema assertions.
- **Trade-off:** Fast execution and deterministic assertions versus inability to test live infrastructure routing and token life cycles.
- **Failure case:** Strict parsers crashing on unknown backend fields or unhandled new enum values.
- **Production solution:** Consumer-driven contracts in CI, `ignoreUnknownKeys`, enum fallback handling, and a focused suite of smoke E2E tests.

## Deep-dive talking points

- **CDC (Consumer-Driven Contracts):** Why the consumer dictates the contract based on what fields it actually uses.
- **MockWebServer Mechanics:** Enqueuing raw HTTP responses to test Retrofit interceptors, converters, and error adapters.
- **Kotlinx Serialization Robustness:** The necessity of `ignoreUnknownKeys = true` and custom enum deserializers in production apps.
- **Contract vs Functional Test:** Contract tests assert data shape and protocol agreement; functional tests assert user-visible screen behavior.

## Follow-up questions

- [TST-01](../tst-01/): What do end-to-end tests provide that contract tests cannot? **Answer:** E2E tests validate deployed infrastructure, live authentication tokens, platform permissions, and multi-screen user journeys.
- [TST-12](../tst-12/): What specifically does MockWebServer test in an Android test suite? **Answer:** It tests OkHttp interceptors, Retrofit converters, JSON serialization, HTTP status code error mapping, and retry policies.

## Self-check rubric

- Can I explain the cost/speed/confidence trade-offs of the Test Pyramid?
- Can I write a complete MockWebServer contract test verifying request headers and response serialization?
- Can I explain why `ignoreUnknownKeys = true` and enum fallbacks are critical in production contracts?
- Can I describe how Consumer-Driven Contract testing works with Pact in a CI/CD pipeline?
- Can I clearly articulate the complementary roles of contract tests and E2E tests?

## References and reviewed-on date

- [Android testing fundamentals](https://developer.android.com/training/testing/fundamentals) — test pyramid and scope.
- [OkHttp MockWebServer](https://github.com/square/okhttp/tree/master/mockwebserver) — testing HTTP and REST clients.
- [Martin Fowler: Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html) — testing strategies and contract boundaries.

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
