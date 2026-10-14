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

كيف تتكامل مكتبتا Retrofit و OkHttp داخل طبقة الشبكة (Networking Stack) في تطبيقات Android؟

1. تقسيم المسؤوليات المعماري:
   - **OkHttp (طبقة النقل والاتصال الفعلي - Transport & HTTP Engine)**:
     * يعمل في المستوى المنخفض (Socket Level).
     * يدير تجميع الاتصالات (Connection Pooling) لإعادة استخدام اتصالات TCP ومصافحات TLS وتجنب تكلفة إنشائها المتكررة.
     * يدير الـ Interceptors (إضافة التوكنز، ضغط GZIP، الـ Logging، و Caching).
     * يتعامل مع الـ Timeouts، وفشل الاتصال، وإعادة المحاولة على مستوى الشبكة.
   - **Retrofit (طبقة التحويل والواجهة البرمجية - High-Level Declaration & Serialization Engine)**:
     * يعمل فوق OkHttp.
     * يحول واجهات Kotlin (`interface ApiService`) المعلمة بتعليقات مثل `@GET("users/{id}")` إلى طلبات HTTP فعلية عبر OkHttp.
     * يدير المحولات (Converter Factories مثل Kotlinx Serialization أو Moshi) لتحويل نصوص الـ JSON إلى كائنات Kotlin، ومحولات الاستدعاء (Call Adapters مثل Coroutines `suspend` أو `Result<T>`).

2. الحدود المعمارية الصارمة (Strict Architectural Boundaries):
   - لا يجب أن تصل كائنات Retrofit أو OkHttp أو كلاسات الـ DTOs إلى طبقة الـ UI أو الـ ViewModels.
   - طبقة الـ Repository تعزل الـ Network بالكامل: تستدعي Retrofit، وتعالج الأخطاء، وتحول الـ DTOs إلى Domain Models نقية ومستقرة.

## Practical walkthrough

المقارنة العملية لتوزيع الأدوار بين OkHttp و Retrofit وطبقة الـ Repository:
```kotlin
// 1. إعداد OkHttp (المسؤول عن النقل، الأمان، والتفاصيل الفيزيائية للشبكة):
val okHttpClient = OkHttpClient.Builder()
    .connectTimeout(15, TimeUnit.SECONDS)
    .readTimeout(20, TimeUnit.SECONDS)
    .addInterceptor(AuthHeaderInterceptor(tokenProvider))
    .certificatePinner(CertificatePinner.Builder().add("api.example.com", "sha256/...").build())
    .build()

// 2. إعداد Retrofit (المسؤول عن تجريد الـ HTTP والـ Serialization):
val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .client(okHttpClient) // OkHttp هو المحرك الحقيقي تحت الغطاء
    .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
    .build()

interface UserApiService {
    @GET("v1/users/{id}")
    suspend fun getUserProfile(@Path("id") userId: String): UserDto // تعبير نظيف عن العقد
}

// 3. طبقة الـ Repository: العازل الحامي للـ Domain والـ UI:
class UserRepositoryImpl @Inject constructor(
    private val api: UserApiService
) : UserRepository {
    override suspend fun getUser(id: String): Result<User> = runCatching {
        api.getUserProfile(id).toDomain() // تحويل DTO إلى Domain Model
    }
}
```

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

OkHttp handles low-level transport: socket pooling, TLS handshakes, interceptors, and caching. Retrofit sits on top, abstracting HTTP requests into type-safe Kotlin interfaces and serializing JSON payloads via Moshi or Kotlinx Serialization. The Repository layer isolates both from the UI, converting DTOs into pure domain models.

## Interview answer — structured

In a production Android networking stack, Retrofit and OkHttp divide responsibilities cleanly across presentation and transport layers.

First, with OkHttp (Transport & Protocol Layer), operates at the socket level. It manages TCP connection pooling, HTTP/2 multiplexing, TLS handshakes, certificate pinning, and caching. Its interceptor pipeline (`Application` and `Network` interceptors) centralizes cross-cutting concerns like OAuth authentication, telemetry logging, and gzip compression. Next, with Retrofit (Type-Safe API Abstraction), built directly on top of OkHttp. It translates annotated Kotlin interfaces (`@GET`, `@POST`) into concrete OkHttp HTTP calls using dynamic proxies and reflection. It leverages Converter Factories (Kotlinx Serialization, Moshi) to deserialize JSON into Data Transfer Objects (DTOs), and Call Adapters to support Kotlin coroutines (`suspend fun`).
Finally, with Architectural Isolation, neither Retrofit nor OkHttp types should ever leak into ViewModels or UI composables. A Repository orchestrates network calls, intercepts HTTP exceptions, and maps network DTOs into stable, immutable Domain entities.


## Interview answer — deep senior

A critical distinction senior engineers inspect under the hood is the difference between **OkHttp Application Interceptors and Network Interceptors**.

First, application Interceptors (`addInterceptor`) is executed once per high-level call at the very top of OkHttp's interceptor chain. They observe the request before redirects, retries, and caching. This is the only safe location for authentication token injection and high-level request tracing. Finally, network Interceptors (`addNetworkInterceptor`) is executed at the wire level just before data is written to the socket. If an HTTP request encounters a 302 redirect or is served directly from OkHttp's local HTTP disk cache, network interceptors will not execute, or may execute multiple times for retried requests. They are meant strictly for monitoring wire traffic and modifying transport headers (e.g., inspecting transfer encoding or cache headers).


## How to answer in the interview

- **Why:** Separate transport success from valid application data.
- **How:** Trace UI → repository → Retrofit service → reusable OkHttp client and converter.
- **Trade-offs:** Use raw OkHttp only for unusual transport needs, not ordinary typed endpoints.
- **Failure cases:** Name malformed 200 bodies, token logs, and unsafe POST replay.
- **Production solution:** Mock-server tests cover headers, error mapping, cancellation and release behavior.

## Deep-dive talking points

Trace one request from UI to repository/service/client and classify transport, HTTP and domain errors.

## Follow-up questions

- **Interviewer:** "Why shouldn't you log authentication tokens in OkHttp Logging Interceptor in production?"
  **Answer:** "Logging headers in production dumps sensitive JWTs or session credentials into Android Logcat, exposing user accounts to any app with log-reading permissions or crash reports."

- **Interviewer:** "What happens if a Retrofit endpoint returns HTTP 404 in a suspending function?"
  **Answer:** "Retrofit throws an `HttpException` with code 404, which must be caught via `runCatching` or a custom CallAdapter; it does not return null by default."

## Self-check rubric

Can I name each layer, classify failures, reuse transport and avoid credential logging?

## References and reviewed-on date

- [Retrofit project](https://github.com/square/retrofit) — typed HTTP client.
- [OkHttp documentation](https://lysine.dev/okhttp/) — transport features.
- [Android network security](https://developer.android.com/privacy-and-security/security-config) — platform TLS configuration.

Technically reviewed against primary documentation on 2026-10-13.
