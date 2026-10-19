---
id: "DAT-01"
question: "How do Retrofit and OkHttp fit into a typical Android networking stack?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "A"
phase: 3
priority: "P1"
order: 258
editorial_status: "reviewed"
---

# DAT-01

## Original interview question

How do Retrofit and OkHttp fit into a typical Android networking stack?

## What the interviewer evaluates

Place Retrofit API declarations over OkHttp transport and define repository/error boundaries.

## Concept and technical explanation

OkHttp is the HTTP client that handles connections, TLS, interceptors, timeouts, and optional cache. Retrofit sits above a configured call factory such as OkHttp: it maps annotated service interfaces to calls and uses configured converter factories for body serialization. JSON conversion is not automatic without an appropriate converter. A repository can translate HTTP, transport, and parsing outcomes and map DTOs into a contract suited to the rest of the app; a separate domain model is useful when it protects a real boundary, not a compulsory class for every response.

## Practical walkthrough (English)

A shared OkHttpClient configures TLS, timeouts, and an interceptor that attaches an authorization header without logging secrets. Retrofit uses that client and a chosen JSON converter for a UserApi service interface. A repository calls the service, distinguishes a missing user from offline or malformed data, and maps the required fields to a UI or domain model. A retry for a write request needs an actual backend idempotency contract. This is an architecture sketch rather than a standalone compilable snippet.

## Explanation in Arabic

`OkHttp` هو HTTP Client اللي بيبعت الطلبات: اتصال، TLS، Connection Pool، Interceptor Chain، Timeouts، وCache لو اتضبطت. `Retrofit` طبقة فوقه: بتحوّل API Interface فيها `@GET` و`@POST` إلى Calls، وتستخدم Converter Factory لو عايز تحول JSON لـ DTO. Retrofit مش هيحول أي JSON لوحده من غير Converter مناسب.

الـ Repository بتدي Feature عقد يناسبها: تنادي API، تفسر Network وHTTP وParsing Failures، وتحول DTO لشكل مناسب للـ Domain أو UI حسب حجم التطبيق. مش لازم تعمل Domain Model منفصلة لكل DTO بلا سبب، لكن ما تخليش UI مربوطة بتفاصيل Server Response متغيرة.

`Suspend Function` في Retrofit تساعد Coroutine تستنى Response من غير حبس Main Thread، لكن لا تعني إن الطلب مضمون أو إن Cancellation تلغي أثر حصل على السيرفر. ولو حوّلت Errors لـ `Result`، احذر `runCatching` العادية لأنها تمسك `CancellationException` كمان؛ سيب Cancellation تعدّي بدل ما تحولها لفشل Business عادي.

## Practical walkthrough

في شاشة Profile، الـ `OkHttpClient` مشترك ومهيأ بـ TLS وTimeouts وInterceptor يضيف Authorization Header من Token Provider. `Retrofit` تستخدمه وتعرّف `suspend fun getProfile(id): ProfileDto` مع Converter مناسب. الـ Repository تحول DTO إلى `ProfileUiData` أو Domain Model وتترجم 404 وOffline وMalformed JSON إلى نتائج مفهومة للـ ViewModel. لو Token انتهت، Authenticator أو مسار Renewal يتعامل معها بعقد سيرفر واضح؛ ما تعملش Retry عشوائية لأي POST.

## Why it matters and how it works

A Retrofit suspend service delegates network I/O to its configured OkHttp client; an interceptor can attach request metadata and an authenticator can respond to 401 under a documented server contract. The repository maps transport, HTTP and parsing failures separately. Use one appropriately configured client per backend/session policy rather than constructing one for every request.

## Worked example

Conceptual Android snippet. The app provides `UserDto` and a matching `converter-gson` dependency; the base URL must be trusted HTTPS. The repository still validates `UserDto` before mapping it to a domain user.

```kotlin
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET

interface UserApi { @GET("users/me") suspend fun me(): UserDto }
val http = OkHttpClient.Builder().build()
val api = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .client(http)
    .addConverterFactory(GsonConverterFactory.create())
    .build()
    .create(UserApi::class.java)
```

## Trade-offs and decision criteria

Retrofit reduces API boilerplate; OkHttp remains responsible for transport behavior. A raw OkHttp client can be simpler for unusual protocols; WebSockets use an appropriate streaming contract. Converter and interceptor configuration affect error handling and release R8 behavior.

## Failure modes

Creating a client per request loses connection pooling. An interceptor that logs Authorization leaks credentials. A retry interceptor that blindly replays POST can duplicate writes. A suspend function does not remove the need for timeout and cancellation tests.

## Production perspective

A bank app injects a configured OkHttp client with TLS policy and safe telemetry, Retrofit API interfaces, and a repository that exposes typed domain results. Mock server tests verify headers, errors, cancellation and no token leakage.

## Interview answer — short

OkHttp is the HTTP engine for connections, TLS, interceptors, and timeouts. Retrofit maps an annotated API interface to calls over a configured client and uses converter factories when body serialization is needed. A repository can translate DTOs and HTTP or transport failures into an app-facing contract. Share appropriately configured clients for connection reuse and avoid logging credentials or retrying writes without server support.

## Interview answer — structured

I separate three responsibilities. OkHttp is the HTTP client: it handles connection reuse, TLS, timeouts, and interceptors. Retrofit declares endpoint methods on an interface and creates calls that use that client. To deserialize JSON into DTOs, I configure an appropriate converter; Retrofit does not infer arbitrary JSON parsing without one.

A repository can call the service, distinguish HTTP errors from connectivity and parsing errors, and expose a model suitable for the feature. I avoid coupling a Compose screen to a changing server DTO, but I do not create a domain class for every field if it adds no useful boundary.

In production I share configured OkHttp clients, keep tokens out of logs, and test headers, failures, and cancellation with a mock server. A suspend service method does not prove a remote write was cancelled. Blindly retrying POST in an interceptor can duplicate an effect unless the backend defines an idempotency contract.

## Interview answer — deep senior

OkHttpClient owns the HTTP transport configuration: connection pool, DNS, TLS, interceptors, timeouts, and optional caching. Reusing a configured client lets requests share connections; creating a new client per request defeats that and scatters policy. Interceptors can attach safe metadata but also see sensitive headers and bodies, so logging and retry behavior need careful review.

Retrofit parses service-interface annotations, builds calls through the configured call factory, and uses converter factories for request and response bodies. Return shape matters: a direct body-returning suspend function and a Response<T> return expose HTTP status differently. Failures may come from transport, non-2xx HTTP, conversion, or business rules inside a nominally successful body. The repository should preserve that distinction where the product needs it and map DTOs when doing so shields a stable boundary.

Coroutine cancellation can cancel client waiting but cannot prove the server did not execute a submitted write. Kotlin runCatching captures any Throwable, including CancellationException, so using it around a suspend call without rethrowing cancellation can turn cancellation into an ordinary UI failure. Retried writes require backend idempotency or a status-reconciliation path.

A useful test suite checks authorization headers, 401 handling, 404, malformed JSON, timeouts, cancellation, and the absence of token logging with MockWebServer or an equivalent fake server. Timeouts and retry rules should reflect actual backend and mobile-network behavior, not universal constants.

## How to answer in the interview

- **Why:** Separate transport success from valid application data.
- **How:** Trace UI → repository → Retrofit service → reusable OkHttp client and converter.
- **Trade-offs:** Use raw OkHttp only for unusual transport needs, not ordinary typed endpoints.
- **Failure cases:** Name malformed 200 bodies, token logs, and unsafe POST replay.
- **Production solution:** Mock-server tests cover headers, error mapping, cancellation and release behavior.

## Deep-dive talking points

Trace one request from UI to repository/service/client and classify transport, HTTP and domain errors.

## Follow-up questions

- **Interviewer:** "Does Retrofit deserialize JSON automatically?"
  **Answer:** "Only with an appropriate configured converter factory. Retrofit maps service methods to calls; body conversion is a separate configuration."

- **Interviewer:** "Why share OkHttpClient?"
  **Answer:** "Shared configuration and connection reuse. A client per request loses pooling benefits and scatters timeout and interceptor policy."

- **Interviewer:** "What is risky about runCatching around suspend calls?"
  **Answer:** "It catches CancellationException as a Throwable. Rethrow cancellation instead of reporting it as an ordinary business failure."

## Self-check rubric

Can I name each layer, classify failures, reuse transport and avoid credential logging?

## References and reviewed-on date

- [Retrofit project](https://github.com/square/retrofit) — service interfaces and converters.
- [OkHttp project](https://github.com/square/okhttp) — client reuse and interceptors.
- [Kotlin runCatching](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin/run-catching.html) — Throwable capture.

Technically reviewed against primary project documentation on 2026-10-19.
