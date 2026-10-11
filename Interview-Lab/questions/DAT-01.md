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

Conceptual Android snippet; converter dependency and `UserDto` are application-specific, and base URL must be trusted HTTPS.

```kotlin
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.http.GET

interface UserApi { @GET("users/me") suspend fun me(): UserDto }
val http = OkHttpClient.Builder().build()
val api = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .client(http)
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

“Retrofit defines typed HTTP endpoints and conversion; OkHttp performs transport, connections, interceptors and timeouts. I place domain mapping and retry policy in a repository, and keep authentication and logging safe.”

## Interview answer — structured

“In a common Android stack, Retrofit makes annotated service interfaces and handles conversion from wire payloads, while OkHttp executes HTTP with connection pooling, TLS, caching and interceptors. I configure a reusable client, not one per call. A repository sits above the service to map DTOs, HTTP failures and domain state. An auth interceptor can add a token, but refresh on 401 needs careful serialization and server rules. I test actual requests with a mock server and avoid logging credentials. Retrofit reduces API boilerplate; OkHttp remains responsible for transport behavior. A raw OkHttp client can be simpler for unusual protocols; WebSockets use an appropriate streaming contract. Converter and interceptor configuration affect error handling and release R8 behavior. A bank app injects a configured OkHttp client with TLS policy and safe telemetry, Retrofit API interfaces, and a repository that exposes typed domain results.”

## Interview answer — deep senior

“I separate three concerns: transport, protocol and application meaning. OkHttp owns sockets, TLS, timeouts and interceptors; Retrofit turns a service interface into calls and delegates to OkHttp; the repository translates responses into stable domain contracts. A 200 response with invalid data is not the same as a transport timeout, and a 401 requires session-aware refresh logic rather than a generic retry. I reuse a configured client for pooling, inject dependencies for tests, and review logging and R8 behavior in release. For a financial write I do not let a generic interceptor replay requests without idempotency and reconciliation. A Retrofit suspend service delegates network I/O to its configured OkHttp client; an interceptor can attach request metadata and an authenticator can respond to 401 under a documented server contract. The repository maps transport, HTTP and parsing failures separately. Use one appropriately configured client per backend/session policy rather than constructing one for every request. Creating a client per request loses connection pooling. An interceptor that logs Authorization leaks credentials. A retry interceptor that blindly replays POST can duplicate writes. A suspend function does not remove the need for timeout and cancellation tests. A bank app injects a configured OkHttp client with TLS policy and safe telemetry, Retrofit API interfaces, and a repository that exposes typed domain results.”

## Deep-dive talking points

Trace one request from UI to repository/service/client and classify transport, HTTP and domain errors.

## Follow-up questions

- [DAT-03](../dat-03/): Where are network deadlines set? **Answer:** OkHttp call/connect/read/write timeout settings plus app-level deadline as needed.
- [DAT-09](../dat-09/): Where does refresh belong? **Answer:** a coordinated auth boundary, not every UI caller.

## Self-check rubric

Can I name each layer, classify failures, reuse transport and avoid credential logging?

## References and reviewed-on date

- [Retrofit project](https://github.com/square/retrofit) — typed HTTP client.
- [OkHttp project](https://github.com/square/okhttp) — transport features.
- [Android network security](https://developer.android.com/privacy-and-security/security-config) — platform TLS configuration.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
