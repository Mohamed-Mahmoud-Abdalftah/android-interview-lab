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

## Concept and technical explanation

The Test Pyramid is a foundational software engineering framework, originally popularized by Mike Cohn, that dictates the strategic distribution of automated tests across an enterprise application. The pyramid prescribes a broad base of fast, deterministic, inexpensive unit tests (comprising approximately 70-80% of test volume), a middle tier of integration and component tests (15-20%), and a narrow apex of end-to-end and UI instrumentation tests (5-10%). Contract Testing sits at the critical integration boundary between mobile client applications and backend microservices. Rather than spinning up heavyweight end-to-end device environments against live staging servers, contract testing uses tools like Pact or JSON schema validators to establish and verify explicit, versioned agreements between client serialization models and backend API responses on the JVM.

## Practical walkthrough (English)

Verifying consumer-driven contract agreements using JSON Schema and MockWebServer:
```kotlin
// 1. Consumer Contract Specification (Client Model Expectation)
@Serializable
data class UserContractDto(
    val id: String,
    val email: String,
    val isVerified: Boolean // Contract requires non-null boolean!
)

// 2. JVM Contract Verification Test using MockWebServer
class UserApiContractTest {
    private val mockWebServer = MockWebServer()
    private lateinit var api: UserApiService

    @Before
    fun setup() {
        mockWebServer.start()
        api = Retrofit.Builder()
            .baseUrl(mockWebServer.url("/"))
            .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
            .build()
            .create(UserApiService::class.java)
    }

    @After
    fun tearDown() = mockWebServer.shutdown()

    @Test
    fun contractVerification_matchesBackendAgreement() = runTest {
        // Enforce shared Pact contract fixture
        val contractJson = "{"id": "usr_101", "email": "dev@company.com", "isVerified": true}"
        mockWebServer.enqueue(MockResponse().setBody(contractJson).setResponseCode(200))

        val result = api.getUser("usr_101")

        assertEquals("usr_101", result.id)
        assertEquals("dev@company.com", result.email)
        assertTrue(result.isVerified)
    }
}
```

## Explanation in Arabic

ما هو هرم الاختبارات (Test Pyramid) في أندرويد، وأين تقع اختبارات التعاقد (Contract Tests) ضمن هذا الهرم؟

1. هرم الاختبارات الكلاسيكي في أندرويد (The Android Testing Pyramid):
   - **القاعدة (Unit Tests - 70%)**: أكبر عدد من الاختبارات. سريعة، رخيصة، تختبر منطق الأعمال المنعزل على JVM (ViewModels, UseCases, Repositories).
   - **الوسط (Integration Tests - 20%)**: عدد متوسط. تختبر تفاعل المكونات (Room DB, OkHttp Interceptors, WorkManager).
   - **القمة (UI & E2E Tests - 10%)**: أقل عدد من الاختبارات. بطيئة، مكلفة، تختبر أهم مسارات المستخدم الحرجة (Critical User Journeys مثل تسجيل الدخول وإتمام الدفع) على أجهزة حقيقية.

2. أين تقع اختبارات التعاقد (Contract Tests)؟
   - تقع في **طبقة الـ Integration Tests في منتصف الهرم**.
   - **وظيفتها**: التحقق من أن العقد المتفق عليه بين تطبيق الموبايل وخادم الـ Backend (الـ API Request & Response JSON Schema) لم ينكسر!
   - بدلاً من تشغيل اختبار E2E بطيء يتصل بسيرفر حقيقي، يقوم الـ Contract Test بفحص الـ Payload مقابل مواصفات الـ API (مثل Pact أو WireMock) على الـ JVM المحلي في ثوانٍ معدودة!

3. الفائدة الجوهرية لاختبارات التعاقد:
   - تمنع كسر التطبيق في الإنتاج عندما يقوم فريق الـ Backend بحذف أو تعديل حقل في الـ JSON دون إعلام فريق الموبايل.

## Practical walkthrough

تنفيذ Contract Test باستخدام MockWebServer للتحقق من توافق الـ JSON Schema مع كلاسات الـ DTO:
```kotlin
class ApiContractTest {
    private lateinit var mockWebServer: MockWebServer
    private lateinit var apiService: UserApiService

    @Before
    fun setup() {
        mockWebServer = MockWebServer()
        apiService = Retrofit.Builder()
            .baseUrl(mockWebServer.url("/"))
            .addConverterFactory(MoshiConverterFactory.create())
            .build()
            .create(UserApiService::class.java)
    }

    @Test
    fun `user profile response contract satisfies expected domain schema`() = runTest {
        // محاكاة استجابة الـ JSON المعتمدة في مواصفات الـ OpenAPI:
        val contractJson = """
            {
                "user_id": "usr_9988",
                "email": "dev@example.com",
                "is_active": true
            }
        """.trimIndent()

        mockWebServer.enqueue(MockResponse().setResponseCode(200).setBody(contractJson))

        val response = apiService.getUserProfile("usr_9988")
        
        // التحقق من أن السيريالايزر قرأ الحقول بنجاح دون أي تعارض في الأنواع:
        assertEquals("usr_9988", response.id)
        assertEquals("dev@example.com", response.email)
        assertTrue(response.isActive)
    }

    @After
    fun tearDown() = mockWebServer.shutdown()
}
```

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

The test pyramid distributes tests strategically: 70-80% fast, isolated unit tests at the base, 15-20% integration tests in the middle, and 5-10% end-to-end UI tests at the peak. Contract tests fit at the client-server integration boundary. Using consumer-driven contracts like Pact, they verify that API JSON payloads match client data models and nullability expectations on the JVM, catching breaking backend changes without expensive end-to-end tests.

## Interview answer — structured

The test pyramid is the premier architectural blueprint for maintaining scalable, cost-effective test automation in enterprise mobile engineering.
The pyramid is structured into three primary tiers defined by their execution speed, cost, and fidelity.
At the broad base reside unit tests, representing roughly 70 to 80 percent of the total suite.
Because they execute on the local host JVM in milliseconds without platform overhead, they exhaustively verify business rules, domain invariants, and mathematical calculations.
The middle tier consists of integration tests, accounting for 15 to 20 percent of tests, which validate boundary communication between repositories, local SQLite databases, and networking serialization layers.
At the narrow peak are end-to-end and UI tests, representing only 5 to 10 percent of tests, which validate critical revenue paths on real device emulators.
Contract tests fit squarely at the integration layer between the mobile application and backend microservices.
In microservice architectures, mobile apps frequently break when backend teams rename JSON keys, alter field nullability, or change date formats.
Rather than attempting to detect these regressions via flaky, slow end-to-end tests, teams implement Consumer-Driven Contracts using frameworks like Pact.
The mobile app defines a strict contract specifying the exact JSON schemas and field types it consumes.
Both client and server validate against this shared contract in their respective CI pipelines, catching breaking API changes instantly on the JVM.

## Interview answer — deep senior

Under the hood, the test pyramid and contract testing address the fundamental economics of automated verification: test execution duration, infrastructure compute cost, and test flakiness.
In an inverted test pyramid (an anti-pattern often referred to as the Ice Cream Cone), organizations write hundreds of UI and end-to-end tests while neglecting unit tests.
Because end-to-end tests depend on device emulators, Wi-Fi connectivity, database seeds, and backend staging health, their failure probability compounds exponentially across multiple network hops.
Contract testing neutralizes this systemic flakiness through schema decoupling and deterministic JVM execution.
When using Consumer-Driven Contract testing via tools like Pact or OpenAPI Schema Validation, the mobile client authors an executable contract fixture in JSON format detailing expected endpoints, HTTP methods, headers, and response bodies with explicit Kotlinx Serialization constraints.
During client CI builds, MockWebServer replays the contract file locally, asserting that the Kotlin serialization engine deserializes every field without throwing SerializationException or MissingFieldException.
Simultaneously, the backend CI pipeline downloads the identical contract file from a central Pact Broker and runs a provider verification pass, asserting that the live backend endpoints produce payloads matching the consumer's schema.
If a backend engineer makes a previously mandatory field nullable, the provider contract verification immediately fails in their pull request before any code merges.
This eliminates breaking API regressions across distributed engineering organizations without firing a single mobile emulator.

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

- **Interviewer:** "What is Consumer-Driven Contract Testing?"
  **Answer:** "A paradigm where API consumers (mobile app) define and publish their contract expectations, and provider backends validate those contracts in their CI before deployment."

- **Interviewer:** "Why are Contract Tests faster than End-to-End tests?"
  **Answer:** "They run on the local JVM using mock servers or schema validators, eliminating emulator boot times, network round-trips, and live backend staging dependencies."

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

Technically reviewed against primary documentation on 2026-10-13.
