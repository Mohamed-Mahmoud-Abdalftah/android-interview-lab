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

## Concept and technical explanation

Structural patterns address class and object composition, creating flexible abstractions that allow disparate systems to collaborate seamlessly without architectural friction. Adapter converts the existing interface of an incompatible class into an expected target interface, enabling classes with mismatched signatures to interoperate. Facade provides a simplified, unified high-level interface to a complex subsystem, shielding external consumers from underlying implementation intricacies and reducing subsystem dependencies. Decorator attaches additional responsibilities and dynamic behaviors to an object transparently by wrapping it within an identical interface contract, serving as a flexible alternative to subclassing. Proxy provides a surrogate, placeholder, or access-control intermediary for another object, governing access, lazy initialization, logging, or remote inter-process communication transparently.

## Practical walkthrough (English)

Demonstrating Adapter, Facade, Decorator, and Proxy in Android:
```kotlin
// 1. ADAPTER: Converts third-party vendor signature to domain interface
class VendorPaymentSdk { fun chargeCard(cents: Int, cardNum: String): Boolean = true }
interface PaymentGateway { suspend fun pay(amountDollars: Double): Boolean }

class VendorPaymentAdapter(private val sdk: VendorPaymentSdk) : PaymentGateway {
    override suspend fun pay(amountDollars: Double): Boolean =
        sdk.chargeCard((amountDollars * 100).toInt(), "tokenized_card")
}

// 2. FACADE: Simplifies complex Android Biometric & Keyguard subsystem
class BiometricAuthFacade(private val activity: FragmentActivity) {
    fun authenticate(onSuccess: () -> Unit, onError: (String) -> Unit) {
        // Encapsulates BiometricPrompt, PromptInfo, and Executor complexity
        val prompt = BiometricPrompt(activity, ContextCompat.getMainExecutor(activity),
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) = onSuccess()
                override fun onAuthenticationError(code: Int, err: CharSequence) = onError(err.toString())
            })
        prompt.authenticate(BiometricPrompt.PromptInfo.Builder().setTitle("Login").build())
    }
}

// 3. DECORATOR: Wraps component to dynamically add logging behavior
interface OrderService { suspend fun submitOrder(id: String) }
class LoggingOrderDecorator(private val delegate: OrderService) : OrderService by delegate {
    override suspend fun submitOrder(id: String) {
        println("Submitting order: $id")
        delegate.submitOrder(id) // Delegates execution
        println("Order submitted successfully")
    }
}

// 4. PROXY: Controls lazy initialization and permission validation
class ProtectedDocumentProxy(private val userRole: String) {
    private val realDocument: HeavyDocument by lazy { HeavyDocument() }
    fun read(): String = if (userRole == "ADMIN") realDocument.getContent() else error("Forbidden")
}
```

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

Adapter transforms an incompatible interface into one the client expects. Facade provides a simplified high-level entry point to a complex subsystem. Decorator dynamically enhances an object with additional responsibilities by wrapping it within an identical interface. Proxy controls access to an underlying object, managing lazy instantiation, security checks, or inter-process communication. Each structural pattern wraps an underlying collaborator with a distinct architectural intent.

## Interview answer — structured

Structural patterns resolve composition and integration challenges by providing clear abstraction boundaries between components.
The Adapter pattern acts as a translator between incompatible interfaces. When integrating an external library, legacy module, or hardware SDK whose API does not match your domain contracts, an Adapter wraps the external component and exposes the expected clean interface. In Android, RecyclerView.Adapter is a classic framework example, adapting raw domain lists into ViewHolders.
The Facade pattern provides a simplified, unified interface to a complex collection of interacting classes or subsystems. It reduces coupling by presenting consumers with an ergonomic entry point. In mobile engineering, facades are frequently written around complicated Android system services, such as wrapping BiometricPrompt, KeyguardManager, and Keystore crypto operations behind a clean, single-method authentication service.
The Decorator pattern dynamically adds behavior to an object without modifying the original class or resorting to rigid class inheritance. By implementing the same interface as the wrapped object, the decorator intercepts calls, adds functionality like caching or logging, and forwards execution to the delegate.
The Proxy pattern controls and manages access to an underlying target object. While structurally identical to Decorator, its intent is access control: providing lazy instantiation for expensive resources, verifying user permissions, or managing Android IPC through Binder proxies.

## Interview answer — deep senior

Under the hood, these four structural patterns share a common delegation mechanism: an outer wrapper class holds an internal reference to a target collaborator and delegates method calls. The senior differentiator lies entirely in architectural intent and lifecycle governance.
Adapter changes an interface to resolve an incompatibility between two systems that cannot be modified. It operates at architectural seams, translating third-party SDK models into internal domain models.
Facade creates a new, simplified interface to hide subsystem spaghetti. It does not wrap a single object; it orchestrates multiple interacting classes (network clients, disk caches, encryption ciphers) into a cohesive service, dramatically reducing compilation dependencies across feature modules.
Decorator maintains an identical interface while augmenting runtime behavior. In Android networking, OkHttp Interceptors represent the canonical decorator implementation, where each interceptor wraps request execution to inject auth headers, compress payloads, or log network metrics. Kotlin's by-interface delegation syntax (class AuthClient(inner: Api) : Api by inner) makes decorator authoring zero-boilerplate.
Proxy also maintains an identical interface, but governs the lifecycle and accessibility of the underlying object. In Android's operating system, every AIDL client interface is a remote Proxy (BinderProxy) that marshals method arguments across process boundaries into the system server.
Staff engineers enforce these patterns at architectural boundaries to maintain high cohesion and prevent vendor lock-in across enterprise mobile codebases.

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
