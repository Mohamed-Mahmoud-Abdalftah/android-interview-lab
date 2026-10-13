#!/usr/bin/env python3
"""Generator for DAT-01 through DAT-07 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "dat.json"

DAT_01_07 = [
    {
        "id": "DAT-01",
        "arabic_explanation": (
            "كيف تتكامل مكتبتا Retrofit و OkHttp داخل طبقة الشبكة (Networking Stack) في تطبيقات Android؟\n\n"
            "1. تقسيم المسؤوليات المعماري:\n   - **OkHttp (طبقة النقل والاتصال الفعلي - Transport & HTTP Engine)**:\n     * يعمل في المستوى المنخفض (Socket Level).\n     * يدير تجميع الاتصالات (Connection Pooling) لإعادة استخدام اتصالات TCP ومصافحات TLS وتجنب تكلفة إنشائها المتكررة.\n     * يدير الـ Interceptors (إضافة التوكنز، ضغط GZIP، الـ Logging، و Caching).\n     * يتعامل مع الـ Timeouts، وفشل الاتصال، وإعادة المحاولة على مستوى الشبكة.\n   - **Retrofit (طبقة التحويل والواجهة البرمجية - High-Level Declaration & Serialization Engine)**:\n     * يعمل فوق OkHttp.\n     * يحول واجهات Kotlin (`interface ApiService`) المعلمة بتعليقات مثل `@GET(\"users/{id}\")` إلى طلبات HTTP فعلية عبر OkHttp.\n     * يدير المحولات (Converter Factories مثل Kotlinx Serialization أو Moshi) لتحويل نصوص الـ JSON إلى كائنات Kotlin، ومحولات الاستدعاء (Call Adapters مثل Coroutines `suspend` أو `Result<T>`).\n\n"
            "2. الحدود المعمارية الصارمة (Strict Architectural Boundaries):\n   - لا يجب أن تصل كائنات Retrofit أو OkHttp أو كلاسات الـ DTOs إلى طبقة الـ UI أو الـ ViewModels.\n   - طبقة الـ Repository تعزل الـ Network بالكامل: تستدعي Retrofit، وتعالج الأخطاء، وتحول الـ DTOs إلى Domain Models نقية ومستقرة."
        ),
        "practical_walkthrough": (
            "المقارنة العملية لتوزيع الأدوار بين OkHttp و Retrofit وطبقة الـ Repository:\n"
            "```kotlin\n"
            "// 1. إعداد OkHttp (المسؤول عن النقل، الأمان، والتفاصيل الفيزيائية للشبكة):\n"
            "val okHttpClient = OkHttpClient.Builder()\n"
            "    .connectTimeout(15, TimeUnit.SECONDS)\n"
            "    .readTimeout(20, TimeUnit.SECONDS)\n"
            "    .addInterceptor(AuthHeaderInterceptor(tokenProvider))\n"
            "    .certificatePinner(CertificatePinner.Builder().add(\"api.example.com\", \"sha256/...\").build())\n"
            "    .build()\n"
            "\n"
            "// 2. إعداد Retrofit (المسؤول عن تجريد الـ HTTP والـ Serialization):\n"
            "val retrofit = Retrofit.Builder()\n"
            "    .baseUrl(\"https://api.example.com/\")\n"
            "    .client(okHttpClient) // OkHttp هو المحرك الحقيقي تحت الغطاء\n"
            "    .addConverterFactory(Json.asConverterFactory(\"application/json\".toMediaType()))\n"
            "    .build()\n"
            "\n"
            "interface UserApiService {\n"
            "    @GET(\"v1/users/{id}\")\n"
            "    suspend fun getUserProfile(@Path(\"id\") userId: String): UserDto // تعبير نظيف عن العقد\n"
            "}\n"
            "\n"
            "// 3. طبقة الـ Repository: العازل الحامي للـ Domain والـ UI:\n"
            "class UserRepositoryImpl @Inject constructor(\n"
            "    private val api: UserApiService\n"
            ") : UserRepository {\n"
            "    override suspend fun getUser(id: String): Result<User> = runCatching {\n"
            "        api.getUserProfile(id).toDomain() // تحويل DTO إلى Domain Model\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "OkHttp handles low-level transport: socket pooling, TLS handshakes, interceptors, and caching. Retrofit sits on top, abstracting HTTP requests into type-safe Kotlin interfaces and serializing JSON payloads via Moshi or Kotlinx Serialization. The Repository layer isolates both from the UI, converting DTOs into pure domain models.",
        "best_answer": (
            "In a production Android networking stack, Retrofit and OkHttp divide responsibilities cleanly across presentation and transport layers:\n\n"
            "1. **OkHttp (Transport & Protocol Layer)**: Operates at the socket level. It manages TCP connection pooling, HTTP/2 multiplexing, TLS handshakes, certificate pinning, and caching. Its interceptor pipeline (`Application` and `Network` interceptors) centralizes cross-cutting concerns like OAuth authentication, telemetry logging, and gzip compression.\n\n"
            "2. **Retrofit (Type-Safe API Abstraction)**: Built directly on top of OkHttp. It translates annotated Kotlin interfaces (`@GET`, `@POST`) into concrete OkHttp HTTP calls using dynamic proxies and reflection. It leverages Converter Factories (Kotlinx Serialization, Moshi) to deserialize JSON into Data Transfer Objects (DTOs), and Call Adapters to support Kotlin coroutines (`suspend fun`).\n\n"
            "3. **Architectural Isolation**: Neither Retrofit nor OkHttp types should ever leak into ViewModels or UI composables. A Repository orchestrates network calls, intercepts HTTP exceptions, and maps network DTOs into stable, immutable Domain entities."
        ),
        "deep_answer": (
            "A critical distinction senior engineers inspect under the hood is the difference between **OkHttp Application Interceptors and Network Interceptors**:\n\n"
            "- **Application Interceptors (`addInterceptor`)**: Executed once per high-level call at the very top of OkHttp's interceptor chain. They observe the request before redirects, retries, and caching. This is the only safe location for authentication token injection and high-level request tracing.\n\n"
            "- **Network Interceptors (`addNetworkInterceptor`)**: Executed at the wire level just before data is written to the socket. If an HTTP request encounters a 302 redirect or is served directly from OkHttp's local HTTP disk cache, network interceptors will not execute, or may execute multiple times for retried requests. They are meant strictly for monitoring wire traffic and modifying transport headers (e.g., inspecting transfer encoding or cache headers)."
        ),
        "follow_ups": [
            {
                "question": "Why shouldn't you log authentication tokens in OkHttp Logging Interceptor in production?",
                "answer": "Logging headers in production dumps sensitive JWTs or session credentials into Android Logcat, exposing user accounts to any app with log-reading permissions or crash reports."
            },
            {
                "question": "What happens if a Retrofit endpoint returns HTTP 404 in a suspending function?",
                "answer": "Retrofit throws an `HttpException` with code 404, which must be caught via `runCatching` or a custom CallAdapter; it does not return null by default."
            }
        ]
    },
    {
        "id": "DAT-02",
        "arabic_explanation": (
            "ما هي دوال HTTP (Methods)، وأكواد الحالة الشائعة (Status Codes)، وما هو مبدأ الـ Idempotency الحرج في تطبيقات الهاتف؟\n\n"
            "1. دوال HTTP ودلالاتها المعمارية (HTTP Methods Semantics):\n   - **GET**: قراءة الموارد فقط. آمنة (Safe) ولا يجب أن تحدث أي تغيير في حالة السيرفر، وقابلة للتخزين المؤقت (Cacheable).\n   - **POST**: إرسال بيانات لإنشاء مورد جديد أو تنفيذ عملية غير قابلة للتكرار (مثل خصم رصيد أو طلب شحن). **ليست آمنة وليست Idempotent**.\n   - **PUT**: استبدال مورد موجود بالكامل (Replace/Upsert). دالة **Idempotent**.\n   - **PATCH**: تحديث جزئي لبعض حقول المورد.\n   - **DELETE**: حذف مورد محدد. دالة **Idempotent**.\n\n"
            "2. ما هو الـ Idempotency (خاصية التكرار الآمن) ولماذا هي حرجة للموبايل؟\n   - **التعريف**: العملية تعتبر Idempotent إذا كان تكرار إرسال نفس الطلب $N$ مرة ينتج عنه نفس الأثر تماماً على السيرفر كإرساله مرة واحدة فقط ($f(f(x)) = f(x)$).\n   - **أهميتها في الموبايل**: شبكة الموبايل تنقطع باستمرار (Flaky Networks). إذا أرسل التطبيق طلب `POST /checkout` وانقطع الاتصال قبل وصول الرد، لا يعلم التطبيق هل السيرفر خصم المبلغ أم لا! إذا أعاد التطبيق المحاولة بدون **Idempotency Key**، فقد يُخصم من المستخدم مرتين!\n\n"
            "3. أكواد الحالة الأكثر أهمية في Android:\n   - `200 OK` / `201 Created`: نجاح العملية.\n   - `401 Unauthorized`: التوكن منتهي أو غير صالح (يتطلب تجديد التوكن عبر Refresh Token).\n   - `403 Forbidden`: المستخدم مسجل لكنه لا يملك صلاحية هذا المورد (لا تحاول تجديد التوكن!).\n   - `404 Not Found`: المورد غير موجود.\n   - `409 Conflict`: تعارض في البيانات (مثل تعديل ملف تم تعديله من جهاز آخر - ETag Mismatch).\n   - `429 Too Many Requests`: تجاوز حد الطلبات (يتطلب احترام ترويسة `Retry-After`).\n   - `500/502/503`: أخطاء في السيرفر (تتطلب إعادة المحاولة مع Exponential Backoff)."
        ),
        "practical_walkthrough": (
            "إرسال طلب POST مالي مع Idempotency Key لضمان عدم الخصم المزدوج عند انقطاع الشبكة:\n"
            "```kotlin\n"
            "class PaymentRepositoryImpl @Inject constructor(\n"
            "    private val paymentApi: PaymentApiService,\n"
            "    private val pendingTransactionsDao: PendingTransactionsDao\n"
            ") : PaymentRepository {\n"
            "    override suspend fun chargeOrder(orderId: String, amount: Money): Result<PaymentReceipt> {\n"
            "        // 1. توليد مفتاح تكرار آمن (Idempotency Key) وحفظه محلياً في Room أولاً:\n"
            "        val idempotencyKey = \"pay_${orderId}_${amount.cents}\"\n"
            "        pendingTransactionsDao.recordPending(idempotencyKey, orderId)\n"
            "        \n"
            "        return runCatching {\n"
            "            // 2. إرسال الطلب في الترويسة:\n"
            "            // إذا انقطعت الشبكة وأعاد OkHttp أو WorkManager الإرسال،\n"
            "            // يعرف السيرفر هذا المفتاح ويعيد نفس الإيصال السابق دون خصم جديد!\n"
            "            paymentApi.processCharge(\n"
            "                idempotencyKey = idempotencyKey,\n"
            "                request = ChargeRequest(orderId, amount.cents)\n"
            "            )\n"
            "        }.onSuccess {\n"
            "            pendingTransactionsDao.markConfirmed(idempotencyKey)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "HTTP methods define operation semantics: GET is safe and idempotent, PUT/DELETE are idempotent, POST is non-idempotent. Idempotency guarantees that executing a request multiple times produces the identical server state as executing it once, which is vital on flaky mobile networks to prevent duplicate payments or orders via client-generated Idempotency Keys.",
        "best_answer": (
            "Understanding HTTP methods and idempotency is essential for designing resilient mobile APIs:\n\n"
            "1. **Method Semantics & Idempotency**:\n   - An operation is **idempotent** if making $N$ identical requests has the exact same side-effect on the server as making 1 request ($f(f(x)) = f(x)$).\n   - `GET`, `HEAD`, `OPTIONS` are safe (read-only) and idempotent.\n   - `PUT` (full replacement) and `DELETE` (resource removal) are idempotent. Calling `DELETE /users/42` ten times results in user 42 being deleted, regardless of whether subsequent responses return 204 or 404.\n   - `POST` is **non-idempotent**: calling `POST /orders` five times creates five distinct orders and charges the user five times.\n\n"
            "2. **The Mobile Reality of Flaky Networks**:\n   On cellular networks, connection drops frequently occur *after* the server processes a `POST` write but *before* the client receives the `200 OK` response. If the client retries blindly, duplicate operations occur. Production mobile apps prevent this by attaching a deterministic **`Idempotency-Key` UUID** in request headers, allowing the server to recognize duplicate submissions and return cached receipts without re-executing writes."
        ),
        "deep_answer": (
            "From a protocol perspective, senior engineers handle status codes with explicit architectural responses:\n\n"
            "- **`401 Unauthorized` vs. `403 Forbidden`**: A `401` indicates authentication failure—the OkHttp `Authenticator` should intercept this, pause pending requests, perform a single-flight token refresh, and retry the request. A `403` indicates authorization failure (the user is authenticated, but lacks admin privileges)—**never retry a 403 with a token refresh**, as this triggers an infinite retry loop; navigate to an error state or notify the user.\n\n"
            "- **`429 Too Many Requests`**: Inspect the `Retry-After` header. If the server says `Retry-After: 30`, suspend coroutine execution for 30 seconds rather than retrying immediately with exponential backoff, respecting server capacity and preventing IP bans."
        ),
        "follow_ups": [
            {
                "question": "Does HTTP status code 500 mean the write failed on the server?",
                "answer": "Not necessarily! The server could have written to the database and crashed during response serialization. Client retries must use idempotency keys."
            },
            {
                "question": "Can `PATCH` be idempotent?",
                "answer": "It depends on the payload: `PATCH { \"age\": 30 }` is idempotent; `PATCH { \"incrementAge\": 1 }` is non-idempotent."
            }
        ]
    },
    {
        "id": "DAT-03",
        "arabic_explanation": (
            "ما هي مهلات الاتصال في OkHttp:\n`connectTimeout`، و `readTimeout`، و `writeTimeout`، و `callTimeout`، وما الفرق الجوهري بينها؟\n\n"
            "1. تفصيل كل نوع مهلة في OkHttp:\n   - **`connectTimeout` (مهلة فتح الاتصال)**:\n     * الوقت الأقصى المسموح به لإتمام مصافحة TCP الثلاثية (TCP Handshake) ومصافحة TLS/SSL مع السيرفر.\n     * إذا استغرق فتح السوكيت وقتاً أطول (مثلاً بسبب برج اتصالات ضعيف أو سيرفر معطل)، يتم إطلاق `SocketTimeoutException: Connect timed out`.\n     * القيمة الافتراضية في OkHttp: 10 ثوانٍ.\n   - **`readTimeout` (مهلة قراءة البيانات من السوكيت)**:\n     * الوقت الأقصى بين وصول حزمتين متتاليتين من البيانات (Maximum gap between two data packets).\n     * **ليس الوقت الكلي لتحميل الملف**! طالما أن السيرفر يرسل بايتات بانتظام كل ثانيتين، لن يحدث timeout حتى لو استغرق تنزيل الملف ساعة.\n     * يحدث عندما يتوقف السيرفر عن إرسال البيانات فجأة في منتصف الاتصال.\n   - **`writeTimeout` (مهلة كتابة البيانات إلى السوكيت)**:\n     * الوقت الأقصى بين إرسال بايتين متتاليين إلى السيرفر (مثل رفع صورة أو فيديو كبير).\n   - **`callTimeout` (مهلة الطلب الإجمالية من البداية للنهاية)**:\n     * أُضيفت في OkHttp 3.12.\n     * تضع حداً زمنياً صارماً لكامل دورة حياة الطلب: من استعلام DNS، وفتح الاتصال، والـ Redirects، والـ Authentication Retries، حتى اكتمال قراءة الرد بالكامل.\n     * إذا تجاوزت العملية ككل هذه المهلة، يتم إلغاء الطلب فوراً بـ `InterruptedIOException`.\n\n"
            "2. قاعدة هندسية في التعامل مع الـ Timeouts:\n   - وقوع مهلة قراءة (`readTimeout`) لا يعني أبداً أن السيرفر لم ينفذ العملية! السيرفر قد يكون نفذ العملية في قاعدة البيانات وتأخر فقط في إرسال الرد."
        ),
        "practical_walkthrough": (
            "إعداد مهلات OkHttp المتوازنة لتطبيق إنتاجي:\n"
            "```kotlin\n"
            "val okHttpClient = OkHttpClient.Builder()\n"
            "    // 1. مهلة إنشاء الاتصال ومصافحة الـ TLS:\n"
            "    .connectTimeout(15, TimeUnit.SECONDS)\n"
            "    \n"
            "    // 2. مهلة انتظار وصول الحزمة التالية من السيرفر:\n"
            "    .readTimeout(20, TimeUnit.SECONDS)\n"
            "    \n"
            "    // 3. مهلة إرسال الحزم في الرفع:\n"
            "    .writeTimeout(20, TimeUnit.SECONDS)\n"
            "    \n"
            "    // 4. المهلة الشاملة للطلب ككل (مفيدة للـ Endpoints الحرجة التي لا يجب أن تعلق):\n"
            "    .callTimeout(45, TimeUnit.SECONDS)\n"
            "    .build()\n"
            "\n"
            "// تخصيص مهلة خاصة لعمليات رفع الملفات الكبيرة بدون التأثير على العميل العام:\n"
            "val uploadClient = okHttpClient.newBuilder()\n"
            "    .writeTimeout(120, TimeUnit.SECONDS)\n"
            "    .callTimeout(300, TimeUnit.SECONDS) // مهلة 5 دقائق للرفع بالكامل\n"
            "    .build()\n"
            "```"
        ),
        "quick_answer": "connectTimeout bounds TCP/TLS handshake duration. readTimeout bounds inactivity gaps between incoming data packets. writeTimeout bounds inactivity gaps when transmitting packets. callTimeout sets an absolute, end-to-end deadline spanning DNS, handshakes, retries, and complete response consumption.",
        "best_answer": (
            "OkHttp divides timeouts into granular socket-level phases and a top-level end-to-end deadline:\n\n"
            "1. **`connectTimeout`**: The maximum time allotted to establish a physical connection to the remote host. It includes DNS resolution, TCP handshake, and TLS session negotiation. If the server is unreachable or cellular towers drop the SYN packet, OkHttp aborts with a connection timeout.\n\n"
            "2. **`readTimeout`**: The maximum duration of inactivity allowed between two incoming bytes read from the socket. Crucially, **this is NOT the total download timeout**. A 100MB download taking 10 minutes will never trigger a `readTimeout` as long as data packets continue arriving within the configured threshold.\n\n"
            "3. **`writeTimeout`**: The maximum duration of inactivity allowed when pushing bytes to the socket, essential during large multipart image or video uploads.\n\n"
            "4. **`callTimeout`**: Introduced in OkHttp 3.12 as an absolute upper bound for the **entire HTTP transaction**. It encompasses DNS, redirects, multi-hop proxy chains, authentication retries, and full body reading. If the entire operation exceeds this threshold, OkHttp immediately aborts the call."
        ),
        "deep_answer": (
            "From an error-handling and idempotency perspective, distinguishing between `connectTimeout` and `readTimeout` is vital in production:\n\n"
            "- A **`connectTimeout`** guarantees that **the server never received the request**. The TCP connection never established. Retrying this request immediately (even a `POST` payment request) is 100% safe because no server state was altered.\n\n"
            "- A **`readTimeout`** guarantees that **the server received the request, and may have already committed the database transaction**. The socket timeout occurred only while waiting for the response. Retrying a `readTimeout` blindly on a non-idempotent endpoint risks duplicate operations and double charges.\n\n"
            "Senior architectures treat `readTimeout` on mutating operations as an *uncertain state*, querying the server via an idempotency reconciliation check rather than issuing a raw retry."
        ),
        "follow_ups": [
            {
                "question": "Can you configure timeouts dynamically per individual Retrofit call?",
                "answer": "Yes, by passing a custom OkHttp Interceptor that inspects a custom `@Headers(\"Timeout: 30\")` annotation and clones the client with updated timeouts."
            },
            {
                "question": "What is the consequence of setting `connectTimeout` to 1 second on mobile networks?",
                "answer": "On 3G or congested cellular networks, DNS lookup and TLS 1.3 handshakes regularly take 1.5–3 seconds; an aggressive 1-second timeout causes massive false connection failures."
            }
        ]
    },
    {
        "id": "DAT-04",
        "arabic_explanation": (
            "مقارنة معمارية رفيعة المستوى بين بروتوكولات الاتصال في Android:\nREST و GraphQL و WebSockets، ومتى تختار كل منها؟\n\n"
            "1. REST (Representational State Transfer):\n   - **كيف يعمل**: يعتمد على موارد محددة (Resources) عبر عناوين URL (`/users/123/orders`) ودوال HTTP القياسية (GET, POST, PUT, DELETE).\n   - **المميزات**: معيار عالمي، سهل الفهم، ممتاز في التخزين المؤقت (HTTP Caching عبر ETag و Cache-Control)، واستقرار فائق.\n   - **العيوب**: مشكلة الـ Over-fetching (جلب بيانات زائدة لا تحتاجها الشاشة) والـ Under-fetching (الحاجة لطلب 3 endpoints متتالية لعرض شاشة واحدة).\n\n"
            "2. GraphQL:\n   - **كيف يعمل**: نقطة اتصال موحدة (`/graphql`) يرسل فيها العميل استعلاماً دقيقاً (Query) يحدد فيه شكل الحقول التي يحتاجها فقط.\n   - **المميزات**: يحل مشكلة الـ Over/Under-fetching تماماً. مثالي للشاشات المعقدة التي تجمع بيانات من جداول متعددة في طلب واحد.\n   - **العيوب في الموبايل**: يفقد ميزة الـ Standard HTTP Caching لأن كل الطلبات ترسل كـ `POST`، ويتطلب مكتبات خاصة (مثل Apollo Kotlin)، وصعوبة إدارة حماية وتعقيد الاستعلامات على السيرفر.\n\n"
            "3. WebSockets:\n   - **كيف يعمل**: اتصال ثنائي الاتجاه دائم (Persistent Full-Duplex TCP Connection).\n   - **المميزات**: تبادل بيانات فوري بدون Overhead لترويسات HTTP في كل رسالة.\n   - **متى يُستخدم**: للتطبيقات الحية (Live Chat، التداول المالي الفوري، تتبع حركة السائق على الخريطة في تطبيقات التوصيل).\n   - **التحديات في الموبايل**: استهلاك عالي للبطارية إذا لم يُدار بحذر، وانقطاع الاتصال المتكرر عند تحول الهاتف بين شبكة Wi-Fi وبيانات الجوال، مما يتطلب بروتوكول إعادة اتصال ومزامنة دائم."
        ),
        "practical_walkthrough": (
            "جدول المقارنة واتخاذ القرار الهندسي بين البروتوكولات الثلاثة:\n"
            "```text\n"
            "┌───────────────┬──────────────────────────┬──────────────────────────┬──────────────────────────┐\n"
            "│ المعيار       │ REST                     │ GraphQL (Apollo)         │ WebSockets (OkHttp WS)   │\n"
            "├───────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┤\n"
            "│ نوع الاتصال   │ طلب/استجابة (Stateless)  │ طلب/استجابة (Stateless)  │ اتصال دائم (Full-Duplex) │\n"
            "│ الكاش التلقائي│ ✅ مدعوم بـ HTTP Caching  │ ❌ يتطلب Normalized Cache│ ❌ غير مدعوم             │\n"
            "│ حجم البيانات  │ قد يحتوي على Overfetching│ ✅ الحقول المطلوبة فقط   │ ✅ بيانات خام خفيفة      │\n"
            "│ استهلاك بطارية│ منخفض جداً               │ منخفض                    │ يحتاج إدارة دقيقة للـ Ping│\n"
            "│ أفضل استخدام  │ CRUD، دفع، مستندات، ملفات│ شاشات لوحات تحكم وتجارة  │ شات، تتبع تاكسي، ألعاب   │\n"
            "└───────────────┴──────────────────────────┴──────────────────────────┴──────────────────────────┘\n"
            "```"
        ),
        "quick_answer": "REST uses standard resource endpoints and excels at HTTP caching for typical CRUD apps. GraphQL uses a single endpoint with client-specified queries, eliminating over-fetching for complex data dashboards. WebSockets provide persistent, bidirectional TCP connections for low-latency real-time apps like chat and live vehicle tracking.",
        "best_answer": (
            "Choosing between REST, GraphQL, and WebSockets is driven by data velocity, client flexibility, and caching requirements:\n\n"
            "1. **REST (Standard Resource APIs)**: Best for standard CRUD domains, file uploads, and high-cacheability resources. It leverages native HTTP semantics (status codes, ETags, CDN edge caching). Its weakness on mobile is over-fetching (wasting cellular data on unneeded fields) and under-fetching (making chained requests for relational data).\n\n"
            "2. **GraphQL (Client-Driven Relational Queries)**: Best for rich, multi-entity consumer dashboards (e.g. an e-commerce feed joining user, cart, promotions, and reviews in a single query). The client asks for exact fields, saving mobile bandwidth. However, because all queries use HTTP `POST`, standard HTTP/CDN caching is lost, requiring specialized normalized caching engines (Apollo Kotlin).\n\n"
            "3. **WebSockets (Full-Duplex Real-Time Streams)**: Best for low-latency bidirectional push streams (instant messaging, live bidding, multiplayer games, continuous telemetry). Rather than polling REST endpoints, the server pushes events instantly over an open TCP socket. Mobile implementations must manage heartbeat pings, reconnect state machines, and battery life."
        ),
        "deep_answer": (
            "When architecting **WebSockets on Android**, mobile operating system constraints dictate strict lifecycle governance:\n\n"
            "1. **Doze Mode & Radio State**: Keeping a raw WebSocket open prevents the cellular radio from dropping from full power (DCH) to low-power idle state, rapidly draining battery. In background states, the OS can terminate TCP sockets without firing `onClosing()`. Robust apps close WebSockets when the app enters `ON_STOP`, falling back to Firebase Cloud Messaging (FCM) high-priority push notifications for background delivery.\n\n"
            "2. **The Reconnection State Machine**: Cellular handoffs (switching from Wi-Fi to 5G) drop sockets silently. The Android client must implement an active Ping/Pong heartbeat (e.g. `OkHttpClient.Builder().pingInterval(30, TimeUnit.SECONDS)`) and an exponential backoff reconnect policy that reconciles missed events by querying a REST/Room sync cursor upon reconnect."
        ),
        "follow_ups": [
            {
                "question": "Can you use HTTP/2 Server-Sent Events (SSE) instead of WebSockets?",
                "answer": "Yes. If communication is strictly unidirectional from server to client (e.g. live sports scores or stock tickers), SSE is lighter, runs over standard HTTP, and handles auto-reconnect natively."
            },
            {
                "question": "How does Apollo Kotlin manage caching for GraphQL?",
                "answer": "It provides a Normalized Cache that parses response objects by their `id` or `__typename`, storing entities in SQLite to provide reactive Flow queries similar to Room."
            }
        ]
    },
    {
        "id": "DAT-05",
        "arabic_explanation": (
            "المقارنة المعمارية الدقيقة بين خيارات تخزين البيانات المحلية في Android:\nRoom و DataStore و SharedPreferences:\n\n"
            "1. SharedPreferences (الخيار القديم المهمل):\n   - **كيف يعمل**: يحفظ البيانات كملف XML بسيط في ذاكرة الجهاز.\n   - **العيوب القاتلة في الإنتاج**:\n     * استدعاء `getSharedPreferences()` يقرأ الملف بالكامل في الـ Main Thread بشكل متزامن (Synchronous IO)، مما يسبب UI Jank و ANR Crashes!\n     * دالة `apply()` تكتب في الخلفية ولكن قد تعلق في `Activity.onStop()`، بينما `commit()` تحجب الـ Main Thread.\n     * لا يدعم التفاعل مع Kotlin Coroutines أو تدفق البيانات (No Flow support).\n     * عرضة للـ Runtime ClassCastExceptions ولا يضمن الأمان المالي أو الذري.\n\n"
            "2. DataStore (البديل الحديث للـ Key-Value والإعدادات):\n   - **كيف يعمل**: مبني بالكامل على Kotlin Coroutines و Flow لإدارة البيانات غير المتزامنة.\n   - **نوعان**:\n     * **Preferences DataStore**: بديل مباشر لـ SharedPreferences ولكن بمعالجة غير متزامنة تماماً ودعم للـ Flow ومعالجة الأخطاء.\n     * **Proto DataStore**: تخزين منظم بـ Protocol Buffers يضمن Type-Safety كامل وتوليد كلاسات في وقت التجميع.\n   - **متى يُستخدم**: لإعدادات التطبيق، وحالة الجلسة (Session tokens)، وتفضيلات المستخدم البسيطة.\n\n"
            "3. Room (قاعدة البيانات العلائقية المهيكلة):\n   - **كيف يعمل**: طبقة تجريد فوق SQLite توفر فحص استعلامات SQL في وقت التجميع (Compile-time verification).\n   - **متى يُستخدم**: للبيانات المنظمة والمعقدة، والبحث والفلترة، والعلاقات بين الجداول (Foreign Keys)، والمعاملات الذرية (`@Transaction`)، والتخزين المؤقت للبيانات الضخمة (Offline-first caching)."
        ),
        "practical_walkthrough": (
            "المقارنة العملية بالكود بين DataStore و Room للتخزين المحلي:\n"
            "```kotlin\n"
            "// 1. DataStore: مثالي لتفضيلات المستخدم وحالة الجلسة عبر Flow غير المتزامن:\n"
            "class UserPreferencesStore(private val dataStore: DataStore<Preferences>) {\n"
            "    private val THEME_KEY = booleanPreferencesKey(\"dark_mode_enabled\")\n"
            "    \n"
            "    // قراءة آمنة في الخلفية عبر Flow:\n"
            "    val isDarkMode: Flow<Boolean> = dataStore.data.map { prefs ->\n"
            "        prefs[THEME_KEY] ?: false\n"
            "    }\n"
            "    \n"
            "    // تعديل ذري غير متزامن بدون حجب الـ Main Thread:\n"
            "    suspend fun setDarkMode(enabled: Boolean) {\n"
            "        dataStore.edit { prefs -> prefs[THEME_KEY] = enabled }\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. Room: مثالي للبيانات المنظمة والعلاقات والمعاملات المعقدة:\n"
            "@Entity(tableName = \"orders\")\n"
            "data class OrderEntity(\n"
            "    @PrimaryKey val id: String,\n"
            "    val customerId: String,\n"
            "    val totalAmountCents: Long\n"
            ")\n"
            "\n"
            "@Dao\n"
            "interface OrderDao {\n"
            "    @Query(\"SELECT * FROM orders WHERE customerId = :userId ORDER BY totalAmountCents DESC\")\n"
            "    fun observeUserOrders(userId: String): Flow<List<OrderEntity>> // استعلام SQL متحقق منه في التجميع!\n"
            "}\n"
            "```"
        ),
        "quick_answer": "SharedPreferences is legacy synchronous storage prone to UI thread blocking and ANRs. DataStore is modern asynchronous storage built on Coroutines and Flow, ideal for app settings and user preferences. Room is an SQLite abstraction with compile-time query verification, transactions, and relational queries, designed for structured offline-first domain data.",
        "best_answer": (
            "Modern Android applications eliminate SharedPreferences entirely, choosing between DataStore and Room based on data structure complexity:\n\n"
            "1. **SharedPreferences (Legacy / Deprecated Practice)**: Reads entire XML files into memory synchronously on the UI thread, causing frames drops and ANRs. Write calls (`commit` blocks the main thread; `apply` blocks `onStop` in the Activity lifecycle). It lacks transactional safety, type safety, and reactive observation.\n\n"
            "2. **DataStore (Modern Preferences)**: Built on Kotlin Coroutines and Flow. It operates strictly off the main thread (`Dispatchers.IO`), provides atomic transactional updates via ACID file snapshots, handles disk IO corruption gracefully, and offers compile-time type safety via Proto DataStore. It is ideal for user settings, feature flags, and auth tokens.\n\n"
            "3. **Room (Structured Relational Storage)**: An enterprise SQLite abstraction. Provides compile-time SQL query validation, multi-table joins, relational indexing, schema migrations, and reactive `Flow` emissions triggered by database invalidation. It is the mandatory engine for complex offline-first data, feeds, and shopping carts."
        ),
        "deep_answer": (
            "Neither Room nor DataStore encrypt data on disk by default:\n\n"
            "- SharedPreferences and Preferences DataStore store plain text on disk under `/data/data/com.example/`. On rooted devices or via ADB backup, sensitive data can be read trivially.\n\n"
            "- For **Sensitive Credentials (Auth Tokens, Cryptographic Keys)**, neither standard DataStore nor standard Room is sufficient. Secure architectures utilize **EncryptedSharedPreferences / Jetpack Security**, or store Master Keys in the **Android Keystore System** to encrypt DataStore payloads via Proto DataStore serialization, or configure **SQLCipher** for Room."
        ),
        "follow_ups": [
            {
                "question": "Can DataStore replace Room for caching a list of 5,000 products?",
                "answer": "No. DataStore reads and writes the entire payload atomically on every update; storing thousands of items causes massive IO thrashing and lacks indexing and pagination."
            },
            {
                "question": "How do you migrate existing SharedPreferences to DataStore?",
                "answer": "DataStore provides a built-in `SharedPreferencesMigration(context, PREF_NAME)` parameter passed into the DataStore builder that automatically imports keys on first read."
            }
        ]
    },
    {
        "id": "DAT-06",
        "arabic_explanation": (
            "ما هي مكونات مكتبة Room الأساسية:\n`@Entity`، و `DAO`، و `@Transaction`، و `Migration`، و `Flow Query`، وكيف تعمل تحت الغطاء؟\n\n"
            "1. المكونات الأساسية وتفاصيلها:\n   - **`@Entity` (جدول قاعدة البيانات)**:\n     * كلاس يمثل جدولاً في SQLite (`@Entity(tableName = \"users\")`). كل حقل يمثل عموداً، مع تعريف المفتاح الأساسي `@PrimaryKey` والـ Indices لتحسين سرعة الاستعلامات.\n   - **`DAO` (Data Access Object - منفذ الوصول للبيانات)**:\n     * واجهة (`interface`) تعرف عمليات التفاعل مع قاعدة البيانات (`@Insert`, `@Update`, `@Delete`, `@Query`).\n     * يقوم Room في وقت التجميع بالتحقق من صحة استعلامات الـ SQL المدخلة: لو كتبت اسم جدول أو عمود خاطئ، يفشل الـ Build فوراً!\n   - **`@Transaction` (المعاملة الذرية)**:\n     * تضمن تنفيذ مجموعة من عمليات القراءة والكتابة كوحدة واحدة غير قابلة للتجزئة (Atomic Unit):\n     * إما أن تنجح جميع العمليات وتُثبت في الـ Database (`COMMIT`)، أو تلغى جميعها بالكامل عند حدوث أي Exception (`ROLLBACK`).\n   - **`Migration` (ترقية المخطط)**:\n     * كود تدريجي يعدل هيكل الجداول (`ALTER TABLE ...`) عند الانتقال من إصدار إلى إصدار جديد لقاعدة البيانات دون مسح بيانات المستخدم الحالية.\n   - **`Flow Query` (الاستعلام التفاعلي المباشر)**:\n     * دالة استعلام في الـ DAO تُرجع `Flow<T>`.\n     * يسجل Room مستمعاً على جدول الـ SQLite (عبر `InvalidationTracker`). بمجرد تعديل أو إضافة أي سطر في هذا الجدول، يعيد Room تنفيذ الاستعلام تلقائياً ويبث القائمة المحدثة إلى الـ UI."
        ),
        "practical_walkthrough": (
            "التطبيق العملي لمكونات Room المتكاملة مع الـ Transaction والـ Flow Query:\n"
            "```kotlin\n"
            "// 1. Entity:\n"
            "@Entity(tableName = \"cart_items\")\n"
            "data class CartItemEntity(\n"
            "    @PrimaryKey val itemId: String,\n"
            "    val quantity: Int,\n"
            "    val priceCents: Long\n"
            ")\n"
            "\n"
            "// 2. DAO مع Transaction و Flow Query:\n"
            "@Dao\n"
            "interface CartDao {\n"
            "    // Flow Query: يعيد البث تلقائياً عند أي تعديل في جدول cart_items:\n"
            "    @Query(\"SELECT * FROM cart_items\")\n"
            "    fun observeAllItems(): Flow<List<CartItemEntity>>\n"
            "\n"
            "    @Insert(onConflict = OnConflictStrategy.REPLACE)\n"
            "    suspend fun insertItem(item: CartItemEntity)\n"
            "\n"
            "    @Query(\"DELETE FROM cart_items\")\n"
            "    suspend fun clearCart()\n"
            "\n"
            "    // @Transaction: تضمن حذف السلة القديمة وإدخال العناصر الجديدة كعملية واحدة:\n"
            "    @Transaction\n"
            "    suspend fun replaceCart(newItems: List<CartItemEntity>) {\n"
            "        clearCart()\n"
            "        newItems.forEach { insertItem(it) }\n"
            "        // لو حدث crash في المنتصف، تعود السلة القديمة كما كانت ولا تصبح فارغة أبداً!\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Room translates @Entity to SQLite tables, and DAO interfaces to type-safe SQL operations verified at compile time. @Transaction guarantees all-or-nothing atomicity for multi-step writes. Migration alters schemas between versions preserving user data. Flow queries automatically emit fresh query results whenever InvalidationTracker detects table mutations.",
        "best_answer": (
            "Room structures SQLite database interactions through five core architectural constructs:\n\n"
            "1. **`@Entity`**: Models a SQLite table. Defines primary keys, auto-generation rules, foreign key constraints, and column indexes.\n\n"
            "2. **`DAO` (Data Access Object)**: Declares data interactions. The Room compiler verifies SQL query syntax and column mappings at compile time against Entity properties, preventing runtime SQL crashes.\n\n"
            "3. **`@Transaction`**: Wraps multiple DAO operations within a single SQLite transaction (`BEGIN TRANSACTION ... COMMIT`). If any statement throws an exception, the entire sequence rolls back, preventing inconsistent database states.\n\n"
            "4. **`Migration`**: Explicit migration definitions (`Migration(1, 2)`) executing raw SQL `ALTER TABLE` statements when bumping the database version, preserving existing user data.\n\n"
            "5. **`Flow Query`**: Reactive streams returning `Flow<List<T>>`. Powered by Room's internal `InvalidationTracker`, any insert, update, or delete on the queried table triggers a re-query on a background dispatcher, automatically emitting the new dataset to collectors."
        ),
        "deep_answer": (
            "Under the hood, understanding **Room InvalidationTracker Mechanics** is vital for senior engineers:\n\n"
            "Room does **NOT** observe individual rows; it observes **entire tables**.\n"
            "When Room initializes, it sets SQLite triggers on observed tables. When a write occurs, SQLite increments an internal invalidation counter in `room_master_table` or an in-memory bitset. "
            "The `InvalidationTracker` polls or receives trigger notifications on `Dispatchers.IO`, and dispatches an invalidation signal. The active Flow query re-runs the entire SQL query from scratch and emits the fresh result.\n\n"
            "Crucial Performance Consequence: If you query a 5,000-row table and update just 1 unrelated row in that table, Room re-executes the entire 5,000-row query! "
            "To prevent UI jank in high-frequency update tables, use targeted queries (`WHERE id = :id`), index foreign keys, and split rapidly changing columns into separate tables."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between `@Transaction` on a DAO method and `roomDatabase.withTransaction { }`?",
                "answer": "`@Transaction` is an annotation for DAO methods; `withTransaction` is a coroutine extension function allowing multi-DAO transactions from repositories."
            },
            {
                "question": "Why does a Room Flow query never complete?",
                "answer": "Because it represents an infinite hot reactive stream observing future database mutations; it stays alive until the collecting coroutine scope cancels."
            }
        ]
    },
    {
        "id": "DAT-07",
        "arabic_explanation": (
            "ما هو التطبيق القائم على مبدأ العمل في وضع عدم الاتصال أولاً (Offline-First Application)، وكيف تصمم مسارات القراءة والكتابة الخاصة به؟\n\n"
            "1. المفهوم المعماري الجوهري:\n   - التطبيق الـ Offline-First لا يعتبر انقطاع الشبكة حالة استثنائية (Error State)؛ بل يعتبر وضع عدم الاتصال حالة طبيعية أساسية في تشغيل الموبايل.\n   - **قاعدة ذهبية**: التطبيق يجب أن يفتح فوراً، ويعرض بيانات مفيدة، ويتيح للمستخدم تنفيذ العمليات (مثل حفظ مسودة أو تعديل ملف) حتى لو كان الهاتف في وضع الطيران (Airplane Mode).\n\n"
            "2. مسار القراءة (Read Path - Local Source of Truth):\n   - **الشاشة (UI) تقرأ حصرياً وبشكل دائم من قاعدة البيانات المحلية (Room)** عبر `Flow`.\n   - الـ UI لا تنتظر ولا تستمع مباشرة لرد السيرفر!\n   - يقوم الـ Repository في الخلفية بطلب تحديث البيانات من الـ Network (Remote API) وكتابتها داخل Room. بمجرد الكتابة في Room، يتولى الـ Flow تحديث الـ UI تلقائياً وبسلاسة.\n\n"
            "3. مسار الكتابة (Write Path - Optimistic Writes & Sync Queue):\n   - **الكتابة المتفائلة (Optimistic Write)**: عند ضغط المستخدم على 'حفظ'، يتم حفظ التعديل محلياً في Room فوراً كـ Pending Operation مع توليد معرف محلي فريد (UUID).\n   - يتم إبلاغ المستخدم بالنجاح في الـ UI فوراً خلال 5 ميلي ثانية!\n   - تتولى خدمة خلفية موثوقة (مثل `WorkManager`) مراقبة توفر الشبكة وإرسال العمليات المعلقة إلى السيرفر لاحقاً، مع معالجة النزاعات وحالات انقطاع الاتصال بأمان."
        ),
        "practical_walkthrough": (
            "المخطط المعماري الكامل لمساري القراءة والكتابة في تطبيق Offline-First:\n"
            "```text\n"
            "📖 مسار القراءة (Read Path):\n"
            "┌───────────────┐                  ┌───────────────┐\n"
            "│  UI / Screen  │◄──(observe Flow)─┤ Room Database │ ◄── [Single Source of Truth]\n"
            "└───────────────┘                  └───────▲───────┘\n"
            "                                           │ (write to DB)\n"
            "                                   ┌───────┴───────┐\n"
            "                                   │  Network API  │ (Background Sync)\n"
            "                                   └───────────────┘\n"
            "\n"
            "✍️ مسار الكتابة (Write Path):\n"
            "1. User taps 'Create Note'\n"
            "2. Note saved immediately to Room with status = PENDING_SYNC\n"
            "3. UI updates instantly in 5ms\n"
            "4. WorkManager triggers SyncWorker when NETWORK_CONNECTED constraint met\n"
            "5. SyncWorker calls Server -> on 200 OK -> updates Room status = SYNCED\n"
            "```"
        ),
        "quick_answer": "An offline-first application treats local persistence (Room) as the single source of truth for all UI reads. The UI observes local databases via Flow, background sync workers fetch remote data and update Room, and writes are saved locally first as pending operations and synchronized to the server asynchronously via WorkManager.",
        "best_answer": (
            "An offline-first architecture treats network connectivity as an intermittent enhancement rather than a prerequisite for app operation:\n\n"
            "1. **Read Pipeline (Single Source of Truth)**:\n   - The presentation layer never queries the network directly. UI screens observe Room database entities via reactive Kotlin `Flow`.\n   - Network fetches occur asynchronously in the background. Fresh payloads are written directly into Room. Room's invalidation triggers automatic UI updates.\n\n"
            "2. **Write Pipeline (Optimistic Local Writes)**:\n   - User mutations (e.g. creating a comment or editing an order) are immediately committed to Room with a local status (`SyncStatus.PENDING`) and a deterministic client UUID.\n   - The UI reflects the change in single-digit milliseconds, eliminating network spinners.\n   - A durable background synchronizer (`WorkManager`) observes network constraints, queues pending mutations, and submits them to the backend with idempotency headers.\n\n"
            "3. **Resilience Across Process Death**: Because pending edits live in persistent SQLite storage, killing the app or rebooting the phone does not lose user changes; syncing resumes automatically when connectivity restores."
        ),
        "deep_answer": (
            "The foundational engineering challenge of offline-first systems is **Reconciliation and Conflict Resolution**.\n\n"
            "When multiple devices edit the same entity offline, local and remote states inevitably diverge. A production offline-first engine must define an explicit conflict resolution policy:\n\n"
            "- **Server-Wins / Timestamp-based (Last-Write-Wins - LWW)**: Simple but risks silent data loss if device clocks drift.\n"
            "- **Entity Version Vectors / ETags**: The client sends its base version. If the server's version has advanced, the server rejects the write with HTTP 409 Conflict.\n"
            "- **Field-Level 3-Way Merging**: Merging non-overlapping field edits (e.g., Device A updated `shippingAddress`, Device B updated `phoneNumber`).\n\n"
            "Furthermore, for financial or inventory transactions, offline actions cannot be treated as definitive; they are modeled as **Intentions/Drafts** pending backend settlement."
        ),
        "follow_ups": [
            {
                "question": "Why shouldn't you cache network responses directly in memory instead of Room?",
                "answer": "In-memory caches are wiped when the Android OS kills the process in the background, breaking the offline contract and losing pending user edits."
            },
            {
                "question": "What is an optimistic UI update?",
                "answer": "Updating the UI immediately assuming the network operation will succeed, rolling back or marking as failed only if the server explicitly rejects the transaction."
            }
        ]
    }
]

def main() -> None:
    if DATA_FILE.exists():
        existing = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        by_id = {item["id"]: item for item in existing}
    else:
        by_id = {}

    for item in DAT_01_07:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions DAT-01 to DAT-07. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
