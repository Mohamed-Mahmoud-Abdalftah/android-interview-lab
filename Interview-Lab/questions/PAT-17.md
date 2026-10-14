---
id: "PAT-17"
question: "A global Singleton makes tests order-dependent. How do you redesign ownership?"
topic: "Design Patterns"
code: "PAT"
group: "C"
phase: 2
priority: "P1"
order: 208
editorial_status: "reviewed"
---

# PAT-17

## Original interview question

A global Singleton makes tests order-dependent. How do you redesign ownership?

## What the interviewer evaluates

Redesign global mutable singleton ownership to eliminate test order dependence and lifecycle leaks.

## Explanation in Arabic

الـ Singleton العام القابل للتعديل (Global Mutable Singleton) يجعل الاختبارات تعتمد على ترتيب التنفيذ (Order-Dependent). كيف تعيد تصميم ملكية البيانات (Ownership)؟

1. ما هي مشكلة الـ Global Mutable Singleton؟
   - كلاس معرّف كـ `object UserSession` في Kotlin يحتوي على متغيرات عامة: `var currentUser: User? = null` و `var authToken: String? = null`.
   - **تلوث بيئة الاختبار (State Pollution)**: عند تشغيل Unit Tests على الـ JVM، تعمل جميع الاختبارات في نفس عملية الـ JVM Process. إذا قام `TestA` بتسجيل دخول مستخدم ونسي تفريغ الكائن، فإن `TestB` سيبدأ مع بيانات مستخدم موجودة مسبقاً، مما يؤدي إلى نجاح الاختبار عند تشغيله بمفرده وفشله الغامض عند تشغيل السلسلة كاملة (Flaky & Order-dependent tests).
   - **Memory Leaks & Race Conditions**: إذا احتفظ الـ Singleton بمرجع لـ Context أو Activity، فإنه يسرّب الذاكرة طوال فترة حياة التطبيق، كما أن الوصول المتزامن من Threads متعددة بدون مزامنة يسبب تصادمات بيانات (Data Corruption).

2. كيفية إعادة تصميم الملكية (Redesigning Ownership):
   - **استبدال الـ `object` بـ Class عادي**: تحويل الـ Singleton من كائن ثابت عالمي إلى كلاس عادي يتم حقنه بواسطة Dependency Injection (`@Singleton` Scope في Hilt).
   - **Constructor Injection**: تمرير الـ Session Holder عبر الـ Constructor لكل كلاس يحتاجه.
   - **Test Isolation**: في الـ Unit Tests، يتم إنشاء نسخة جديدة تماماً من الكلاس لكل اختبار على حدة (`@Before fun setup()`), مما يضمن عزل الاختبارات بنسبة 100%.

## Practical walkthrough

المقارنة بين Global Mutable Object وحامل حالة محقون معزول لكل اختبار:
```kotlin
// ❌ فوضى الـ Global Mutable Singleton: اختبارات ملوثة وتعتمد على الترتيب:
object GlobalUserSession {
    var token: String? = null // متغير عام يلوث الـ JVM Process في كل الاختبارات!
    var userId: String? = null
}

// Test A يغير الحالة:
@Test fun testLogin() {
    GlobalUserSession.token = "token_123"
    assertTrue(AuthManager.isLoggedIn())
}
// Test B يفشل لو اشتغل بعد Test A لأنه يتوقع مستخدم غير مسجل:
@Test fun testLoggedOutState() {
    // سيفشل هنا لأن GlobalUserSession.token لا يزال محتفظاً بقيمة token_123 من Test A!
    assertFalse(AuthManager.isLoggedIn())
}

// ✅ الحل النظيف: كلاس عادي محقون بـ Scoped Ownership عبر Constructor Injection:
interface SessionManager {
    fun getToken(): String?
    fun setToken(token: String?)
}

class DefaultSessionManager @Inject constructor(
    private val storage: KeyValueStorage
) : SessionManager {
    private val _token = MutableStateFlow<String?>(null)
    override fun getToken(): String? = _token.value
    override fun setToken(token: String?) { _token.value = token }
}

// في الـ Tests: كل اختبار ينشئ نسخته المستقلة في @Before، عزل تام 100%:
class AuthManagerTest {
    private lateinit var sessionManager: SessionManager
    private lateinit var authManager: AuthManager

    @Before
    fun setUp() {
        sessionManager = FakeSessionManager() // نسخة جديدة طازجة لكل اختبار!
        authManager = AuthManager(sessionManager)
    }
    
    @Test fun testLoggedOutState() {
        assertFalse(authManager.isLoggedIn()) // ينجح دائماً بغض النظر عن الترتيب!
    }
}
```

## Why it matters and how it works

Global mutable state creates hidden dependencies and inter-test coupling. DI with explicit scopes makes ownership and replacement visible; repository persistence handles process death. Stateless singletons are different from shared mutable caches.

## Worked example

JVM illustration:
```kotlin
class SessionStore(initialUser: String? = null) {
    private var user = initialUser
    fun currentUser() = user
    fun update(value: String?) { user = value }
}
```
Each unit test constructs its own store. Production may wrap persistent storage and synchronization; this small class alone is not thread-safe or durable.

## Trade-offs and decision criteria

An injected instance adds wiring but improves isolation and ownership. A stateless `object` may be simplest. If multiple threads access mutable session data, use a proper state holder and synchronization; merely replacing singleton with class does not solve races.

## Failure modes

A test sets `SessionCache.user = "admin"` and forgets reset; a later authorization test passes or fails depending on order. Clear setup per test is a temporary patch; explicit injected owner prevents cross-test state. Server still authorizes.

## Production perspective

A fintech app moves session facts to repository backed by protected storage and server refresh. Features observe typed state; tests inject fresh fake stores; logout/refresh races are tested.

## Interview answer — short

Global mutable singletons (`object` with `var`) persist state across test executions in the same JVM process, causing test order dependence and flakiness. Redesign ownership by turning the singleton into a standard class, injecting it via Constructor Injection, controlling its lifecycle scope through a DI container (like Hilt @Singleton), and creating fresh in-memory instances per test.

## Interview answer — structured

A global mutable singleton (`object Session { var user: User? }`) violates single ownership and destroys test determinism. Because JVM test runners reuse the same classloader process to run multiple test suites, mutations made by Test A persist into Test B. Tests become order-dependent: running Test B alone passes, but running the whole test suite fails.

To fix this, we redesign state ownership.

First, with Demote `object` to a Standard Class, we replace the Kotlin `object` with an interface and a concrete class (`SessionManager`). The class encapsulates its state within thread-safe abstractions like `StateFlow`. Next, with Explicit Constructor Injection, any ViewModel, Repository, or Interactor that needs session information declares `SessionManager` in its constructor. Nothing accesses ambient global state.
Finally, with Container-Managed Scope, in production, the DI container (Hilt) manages a single instance scoped with `@Singleton`. In JVM tests, we instantiate a fresh `FakeSessionManager` in `@Before`, guaranteeing 100% test isolation and determinism.


## Interview answer — deep senior

Beyond test ordering bugs, global mutable singletons introduce severe Android runtime vulnerabilities.

First, with Process Death Vulnerability, when Android terminates an app process in the background due to low memory, static variables are purged. When the user returns, the Activity is recreated, but the global singleton's state is reset to `null`, causing widespread `NullPointerExceptions` or forcing unexpected logouts. Proper ownership means persisting critical state to Room or encrypted DataStore, with the session manager reloading state reactively. Next, with Concurrency and Visibility Hazards, naive global singletons with `var` fields lack memory barriers. If thread A writes `user = newProfile` and thread B reads it on another thread, thread B can observe stale cached CPU register values unless fields are `@Volatile` or guarded by a Mutex.
Finally, with Stateless Utilities vs. State Holders, Kotlin `object` is perfectly appropriate for stateless utilities (math functions, date formatters, serializers). It becomes toxic only when it holds mutable state. By moving state into injected repositories, we gain observability, thread-safety, and test parallelizability.


## How to answer in the interview

- **Why:** Global mutable state creates order dependence and stale accounts.
- **How:** Inject a session-scoped store and tear it down on logout.
- **Trade-off:** Keep stateless singletons; scope mutable session objects narrowly.
- **Failure case:** Test pollution, Activity leak or process-death assumption.
- **Production solution:** Per-test instances, account-switch test and durable recovery path.

## Deep-dive talking points

Diagnose test order dependence, separate stateless singleton, specify owner, persistence and concurrency.

## Follow-up questions

- **Interviewer:** "Is Kotlin `object` always bad in Android?"
  **Answer:** "No. Stateless singletons, single-instance formatters, sealed class objects, and pure utilities are great. It is mutable state (`var`) inside an `object` that causes architectural problems."

- **Interviewer:** "What is the difference between a Singleton Pattern and a DI Singleton Scope?"
  **Answer:** "The Singleton Pattern enforces a single instance globally via a private constructor and static access. DI Singleton Scope lets the container create one instance for the app graph, but the class itself remains a normal class that can be easily instantiated multiple times in tests."

## Self-check rubric

Explain a failing test order, propose injection, and state what must survive process death.

## References and reviewed-on date

- [Kotlin object declarations](https://kotlinlang.org/docs/object-declarations.html) — object lifetime.
- [Android architecture guide](https://developer.android.com/topic/architecture) — persistent data ownership.

Technically reviewed against primary documentation on 2026-10-13.
