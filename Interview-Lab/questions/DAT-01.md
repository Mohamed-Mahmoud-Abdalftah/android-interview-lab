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

## Explanation in Arabic

`Retrofit` بتحوّل annotated Kotlin interface إلى HTTP calls وبتستخدم converters للـJSON؛ `OkHttp` هو الـHTTP client اللي يدير connection pooling, TLS, interceptors, timeouts, cache. الـrepository فوقهم يحوّل DTOs إلى domain models ويحدد error/retry contract. ما نحطش token refresh أو business logic داخل UI، وما نطبعش أسرار في HTTP logs.

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

## Practical walkthrough

لو `UserApi.me()` رجعت 200 بس JSON ناقص `id`، transport نجح لكن mapping للدومين لازم يفشل بشكل واضح؛ ما تحوّلش ده لـ“network unavailable”. جهّز `OkHttpClient` واحد مناسب للbackend عشان connection pool/timeouts/interceptors، وRetrofit service للـendpoint والتَحويل. في repository اعمل validation للـDTO قبل `User` domain model، وارسم contract للأخطاء: I/O، HTTP status، malformed body، unauthorized. Auth header يتضاف في boundary آمنة، لكن refresh ما يدخلش loop في interceptor، وlogging ما تطبعش token أو PII. اختبر request headers وstatus/body بكود mock server وتأكد release variant مع converter/R8.

## Trade-offs and decision criteria

Retrofit reduces API boilerplate; OkHttp remains responsible for transport behavior. A raw OkHttp client can be simpler for unusual protocols; WebSockets use an appropriate streaming contract. Converter and interceptor configuration affect error handling and release R8 behavior.

## Failure modes

Creating a client per request loses connection pooling. An interceptor that logs Authorization leaks credentials. A retry interceptor that blindly replays POST can duplicate writes. A suspend function does not remove the need for timeout and cancellation tests.

## Production perspective

A bank app injects a configured OkHttp client with TLS policy and safe telemetry, Retrofit API interfaces, and a repository that exposes typed domain results. Mock server tests verify headers, errors, cancellation and no token leakage.

## Interview answer — short

“Retrofit defines typed HTTP endpoints and conversion; OkHttp performs transport, connections, interceptors and timeouts. I place domain mapping and retry policy in a repository, and keep authentication and logging safe.”

## Interview answer — structured

“In a common Android stack, Retrofit makes annotated service interfaces and handles conversion from wire payloads, while OkHttp executes HTTP with connection pooling, TLS, caching and interceptors. I configure a reusable client, not one per call. A repository sits above the service to map DTOs, HTTP failures and domain state. An auth interceptor can add a token, but refresh on 401 needs careful serialization and server rules. I test actual requests with a mock server and avoid logging credentials.”

## Interview answer — deep senior

I separate three concerns: transport, protocol and application meaning. OkHttp owns sockets, TLS, timeouts and interceptors; Retrofit turns a service interface into calls and delegates to OkHttp; the repository translates responses into stable domain contracts. A 200 response with invalid data is not the same as a transport timeout, and a 401 requires session-aware refresh logic rather than a generic retry. I reuse a configured client for pooling, inject dependencies for tests, and review logging and R8 behavior in release. For a financial write I do not let a generic interceptor replay requests without idempotency and reconciliation.

For a profile endpoint, I would have Retrofit declare the HTTP shape, OkHttp execute it through one configured client, and the repository validate the DTO. A successful TCP exchange or 200 status does not prove the payload is a usable profile. I map transport loss, HTTP rejection, and malformed response into different domain outcomes because each asks for a different UI action. An authentication header can be added at the client boundary, but a 401 refresh path needs bounded attempts and session coordination. The failure cases are per-call clients losing pooling, logs exposing credentials, or an interceptor replaying a financial POST. I test those with a mock server and a minified build.

## How to answer in the interview

- **Why:** Separate transport success from valid application data.
- **How:** Trace UI → repository → Retrofit service → reusable OkHttp client and converter.
- **Trade-offs:** Use raw OkHttp only for unusual transport needs, not ordinary typed endpoints.
- **Failure cases:** Name malformed 200 bodies, token logs, and unsafe POST replay.
- **Production solution:** Mock-server tests cover headers, error mapping, cancellation and release behavior.

## Deep-dive talking points

Trace one request from UI to repository/service/client and classify transport, HTTP and domain errors.

## Follow-up questions

- [DAT-03](../dat-03/): Where are network deadlines set? **Answer:** OkHttp call/connect/read/write timeout settings plus app-level deadline as needed.
- [DAT-09](../dat-09/): Where does refresh belong? **Answer:** a coordinated auth boundary, not every UI caller.

## Self-check rubric

Can I name each layer, classify failures, reuse transport and avoid credential logging?

## References and reviewed-on date

- [Retrofit project](https://github.com/square/retrofit) — typed HTTP client.
- [OkHttp documentation](https://lysine.dev/okhttp/) — transport features.
- [Android network security](https://developer.android.com/privacy-and-security/security-config) — platform TLS configuration.

Technically reviewed against linked primary documentation on 2026-10-13. Examples are conceptual unless explicitly stated otherwise; no Android device execution is claimed.
