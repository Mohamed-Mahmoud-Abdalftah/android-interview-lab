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

## Concept and technical explanation

Global mutable singletons (such as Kotlin object declarations retaining var properties or static instance holders) introduce hidden shared mutable state across an entire JVM process, causing test order dependence, flaky test suites, and concurrency race conditions. When unit test suites run in a shared test process, modifications made by Test A persist in memory and contaminate the execution environment of Test B. To remediate this defect, software architects redesign state ownership by transforming static objects into ordinary instantiable classes, externalizing their lifecycle management to a Dependency Injection container, enforcing constructor injection, and providing fresh, isolated in-memory instances for every individual test execution.

## Practical walkthrough (English)

Refactoring a global mutable singleton into an isolated, test-friendly dependency:
```kotlin
// BAD ANTI-PATTERN: Global Mutable Singleton (Causes test contamination and order dependence!)
object UserSessionManager {
    var activeUser: User? = null // Persists across all unit tests in the same JVM runner!
    fun logout() { activeUser = null }
}

// REDESIGNED: Ordinary instantiable class with clear contract
interface UserSession {
    val currentUser: User?
    fun updateSession(user: User)
    fun clear()
}

class UserSessionImpl @Inject constructor() : UserSession {
    private var _user: User? = null
    override val currentUser: User? get() = _user
    override fun updateSession(user: User) { _user = user }
    override fun clear() { _user = null }
}

// PRODUCTION: Scoped via DI container (Singleton within Application lifetime)
@Module
@InstallIn(SingletonComponent::class)
abstract class SessionModule {
    @Binds @Singleton
    abstract fun bindSession(impl: UserSessionImpl): UserSession
}

// UNIT TESTS: 100% Isolated, order-independent, parallel test runs!
class UserProfileViewModelTest {
    // Fresh instance created per test method, zero state leakage!
    private val fakeSession: UserSession = UserSessionImpl()
    private val viewModel = UserProfileViewModel(fakeSession)

    @Test fun testLoginUpdatesState() {
        fakeSession.updateSession(User("id_1", "Alice"))
        assertEquals("Alice", viewModel.getCurrentUserName())
    }
}
```

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

A global mutable singleton persists modified state across unit tests running in the same JVM process, making test outcomes depend on execution order. To fix this, redesign ownership by converting the static singleton into an ordinary instantiable class implementing an interface. Enforce constructor injection for all consumers, let a DI container like Hilt manage its application-wide lifecycle scope in production, and instantiate fresh, isolated instances before each test method to guarantee deterministic, order-independent test execution.

## Interview answer — structured

Order-dependent unit tests are a hallmark symptom of architectural contamination caused by global mutable singletons.
When an application uses a Kotlin object or a static Java singleton holding mutable fields, that state lives in the static memory area of the JVM process. When test runners like JUnit execute test classes, all tests within the module frequently share that same JVM process to optimize execution speed. If Test A logs in a user or modifies a configuration flag in the singleton and Test B expects an unauthenticated state, the test suite passes when run in isolation but fails intermittently when run together, creating elusive flaky tests.
Redesigning state ownership requires shifting from global implicit access to explicit scoped dependency injection.
The first step is transforming the static object into a regular class with a private constructor and defining an interface that abstracts its behaviors.
The second step is replacing global static call sites with explicit constructor injection, ensuring that every consuming ViewModel, UseCase, or Repository declares its dependency openly.
The third step is delegating lifecycle ownership to the dependency injection framework. In production, Hilt or Dagger scopes the class to SingletonComponent, ensuring a single shared instance per application runtime.
In test environments, each unit test instantiates a fresh, isolated instance of the class or a lightweight test double during setup, guaranteeing total test independence regardless of execution order.

## Interview answer — deep senior

Under the hood, static singletons circumvent the JVM garbage collection root lifecycle by hanging directly off the ClassLoader's static reference table.
Because the ClassLoader does not unload classes between individual JUnit test methods, any mutable data structure (such as an in-memory HashMap, token cache, or CoroutineScope) attached to a static field remains resident in memory throughout the entire test process. Attempting to fix this by adding a resetForTesting() method is a fragile anti-pattern: it leaks test-only logic into production bytecode, fails to protect against concurrent parallel test runners, and relies on developer discipline to invoke reset in @After teardown methods.
Senior architects resolve this at the structural root by enforcing Inversion of Control. By decoupling the class definition from its instantiation scope, the class becomes a standard transient object whose lifecycle is governed strictly by whatever container or test harness constructs it.
In modern JVM testing architectures, this enables seamless parallel test execution (junit.jupiter.execution.parallel.enabled = true). Because each test method constructs its own isolated object graph via constructor injection, tests run across multiple CPU cores simultaneously without mutex contention, race conditions, or state contamination.
This redesign also eliminates hidden Android framework dependencies. By replacing static context-dependent singletons with injected abstractions, tests execute as pure, blazing-fast JVM tests without requiring Robolectric or device instrumentation overhead.

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
