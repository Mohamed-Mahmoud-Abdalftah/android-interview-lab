---
id: "PAT-04"
question: "Explain Adapter, Facade, Decorator, and Proxy."
topic: "Design Patterns"
code: "PAT"
group: "A"
phase: 2
priority: "P1"
order: 195
editorial_status: "reviewed"
---

# PAT-04

## Original interview question

Explain Adapter, Facade, Decorator, and Proxy.

## What the interviewer evaluates

Differentiate interface conversion, simplified subsystem API, behavior wrapping and controlled access.

## Explanation in Arabic

شرح الأنماط الهيكلية الأساسية: Adapter و Facade و Decorator و Proxy، وأين تظهر في Android:

1. نمط المحول (Adapter Pattern):
   - **الهدف**: التوفيق والربط بين واجهتين غير متوافقتين بحيث تعملان معاً بسلاسة.
   - **في Android**: `RecyclerView.Adapter` يحول قائمة بيانات من الـ Domain (`List<Product>`) إلى `ViewHolders` و `Views` يفهمها نظام Android UI.

2. نمط الواجهة البسيطة (Facade Pattern):
   - **الهدف**: توفير واجهة موحدة وبسيطة لإخفاء تعقيد نظام فرعي ضخم (Subsystem) أو SDK خارجي فوضوي.
   - **في Android**: بناء `LocationTrackerFacade` يخفي تفاصيل `FusedLocationProviderClient`، و `SettingsClient`، وأذونات النظام، مقدماً دالة واحدة بسيطة: `suspend fun getCurrentLocation(): Location`.

3. نمط الزخرفة (Decorator Pattern):
   - **الهدف**: إضافة وظائف وسلوكيات جديدة لكائن موجود ديناميكياً في وقت التشغيل دون اللجوء للوراثة (Subclassing).
   - **في Android**: `OkHttp Interceptors`؛ كل اعتراض يغلف الـ Request ويضيف عليه Headers أو Logging ويعيد تمريره للـ Chain.

4. نمط الوكيل (Proxy Pattern):
   - **الهدف**: توفير كائن بديل أو وكيل يتحكم في الوصول للكائن الأصلي (لأسباب أمنية، كاش، أو استدعاءات عبر العمليات IPC).
   - **في Android**: كائنات الـ **AIDL / Binder Proxies**؛ عند طلب نظام أندرويد لـ `LocationManager`، يحصل التطبيق على Binder Proxy يتولى استدعاء نظام التشغيل عبر الـ IPC.

## Practical walkthrough

أمثلة تمثل الأنماط الهيكلية الأربعة في كود Android:
```kotlin
// 1. ADAPTER: تحويل بيانات النطاق إلى Views:
class ProductAdapter(private val items: List<Product>) : RecyclerView.Adapter<ProductViewHolder>() { ... }

// 2. FACADE: تبسيط SDK معقد خلف دالة واحدة نقية:
class SimpleAudioPlayerFacade(private val exoPlayer: ExoPlayer) {
    fun playStream(url: String) {
        exoPlayer.setMediaItem(MediaItem.fromUri(url))
        exoPlayer.prepare()
        exoPlayer.play()
    }
}

// 3. DECORATOR: تزيين استجابات الشبكة بإضافة ترويسة أمان عبر OkHttp Interceptor:
class AuthHeaderDecorator : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val decoratedRequest = chain.request().newBuilder()
            .addHeader("Authorization", "Bearer token")
            .build()
        return chain.proceed(decoratedRequest)
    }
}

// 4. PROXY: حماية كائن ثقيل وتأجيل تحميله حتى أول استخدام (Virtual Proxy):
val heavyAnalyticsService by lazy { HeavyAnalyticsService() } // كائن Proxy يوفر Lazy Initialization
```

## Why it matters and how it works

Structural patterns control how objects are composed and presented. Selection depends on what changes: incompatible interface, complex subsystem, added cross-cutting behavior, or access to a remote/expensive object.

## Worked example

Conceptual flow: `VendorCallbackAdapter` maps success/error callbacks to `PaymentOutcome`; `CheckoutFacade` exposes `submitAndVerify`; `MetricsGateway` delegates the same `Gateway` API while timing calls; `CachedGatewayProxy` may return fresh cached data. Each needs its own failure and cancellation contract.

## Trade-offs and decision criteria

Wrappers can isolate vendor churn but add stack depth and debugging complexity. A simple adapter is often enough; adding facade/decorator/proxy simultaneously without a real need is ceremony. A proxy cache must define freshness and authority.

## Failure modes

A decorator logs raw card details, leaking sensitive data. Or a proxy returns stale “Paid” status as authoritative. Cross-cutting behavior must honor privacy and server truth; contract tests should catch altered outcomes.

## Production perspective

A checkout integration isolates vendor SDK callbacks in an adapter, provides a small facade to application policy, and adds a metrics decorator that logs only safe codes. Repository still reconciles server status.

## Interview answer — short

Adapter bridges incompatible interfaces (`RecyclerView.Adapter`). Facade provides a simplified unified API over complex subsystems (wrapping ExoPlayer or location APIs). Decorator dynamically wraps objects to add behaviors (`OkHttp Interceptors`). Proxy controls access to another object (Android Binder IPC, Lazy initialization).

## Interview answer — structured

Structural patterns organize relationships and boundaries between collaborating objects:

1. **Adapter (Interface Conversion)**:
   - Converts the interface of a class into another interface clients expect, allowing incompatible classes to work together.
   - *Android Example*: `RecyclerView.Adapter` bridges arbitrary application domain datasets into Android layout `ViewHolders`.

2. **Facade (Unified Simplicity)**:
   - Exposes a simplified, cohesive high-level interface that masks the complexity of an intricate subsystem or convoluted third-party library.
   - *Android Example*: A custom `BillingFacade` wrapping Google Play Billing SDK. The facade encapsulates connection lifecycles, purchase tokens, and acknowledging flows behind simple suspending calls: `suspend fun buy(sku: String): PurchaseResult`.

3. **Decorator (Dynamic Behavioral Augmentation)**:
   - Attaches additional responsibilities to an object dynamically without subclassing, wrapping the original instance.
   - *Android Example*: `OkHttp Interceptors`. Each interceptor wraps HTTP requests and responses, adding caching headers, Gzip compression, or authentication tokens sequentially.

4. **Proxy (Surrogate Access Control)**:
   - Provides a placeholder or surrogate for another object to control access to it (e.g. Remote Proxy, Virtual Proxy for lazy loading, Protection Proxy).
   - *Android Example*: Android's **Binder IPC mechanism**. When an app invokes `LocationManager`, it communicates with an AIDL-generated local client Proxy that serializes calls across process boundaries into system server daemons.

## Interview answer — deep senior

Comparing **Adapter vs Facade vs Decorator**:
- *Adapter* changes an interface to match an existing specification without altering behavior.
- *Facade* defines a *new, simpler* interface to reduce complexity across multiple classes.
- *Decorator* preserves the *same* interface while dynamically enhancing behavior.

In modern Kotlin, the **Decorator pattern** is elegantly built via Class Delegation: `class LoggingRepository(private val delegate: UserRepository) : UserRepository by delegate`. You only override the methods you wish to decorate with logging, while Kotlin delegates all other method calls automatically, cutting boilerplate to near zero.

## How to answer in the interview

- **Why:** Wrappers differ by translation, simplification, added behavior, or access control.
- **How:** Map one vendor SDK through Adapter, Facade, Decorator and Proxy roles.
- **Trade-off:** Each layer adds call-path complexity; keep only useful boundaries.
- **Failure case:** Facade masks unknown payment state or decorator leaks/replays requests.
- **Production solution:** Contract tests and redacted metrics around the vendor boundary.

## Deep-dive talking points

Distinguish intent for four wrappers; test outcome preservation, cancellation and cache authority.

## Follow-up questions

- **Interviewer:** "What is the difference between Facade and Adapter?"
  **Answer:** "An Adapter matches an existing specific interface required by a client. A Facade defines a completely new, simplified interface to make a complex subsystem easier to consume."

- **Interviewer:** "How does Kotlin's `by` keyword implement the Decorator pattern?"
  **Answer:** "By delegating interface methods to an internal wrapped instance (`by delegate`), allowing developers to override only the specific methods they want to decorate."

## Self-check rubric

Given a vendor callback, metrics requirement and cache, select wrapper roles and state one failure per role.

## References and reviewed-on date

- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — structural patterns.
- [Kotlin delegation](https://kotlinlang.org/docs/delegation.html) — forwarding mechanics.

Technically reviewed against primary documentation on 2026-10-13.
