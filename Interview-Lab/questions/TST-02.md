---
id: "TST-02"
question: "Compare fake, mock, stub, spy, and test double."
topic: "Testing, Quality & Reliability"
code: "TST"
group: "A"
phase: 4
priority: "P1"
order: 397
editorial_status: "reviewed"
---

# TST-02

## Original interview question

Compare fake, mock, stub, spy, and test double.

## What the interviewer evaluates

- Distinguishing all test-double roles by behavior.
- When state-based assertions are more robust than interaction assertions.

## Concept and technical explanation

In automated software testing, Test Double is the generic umbrella term coined by Gerard Meszaros for any surrogate object that replaces a production dependency during verification. Within this taxonomy, each double fulfills a specialized architectural role. A Dummy is an inert object passed solely to satisfy method signatures without ever being accessed. A Stub returns hardcoded, canned responses to incoming queries, serving as a passive data fixture without recording invocation history. A Spy wraps a real object or mimics an interface while recording interaction metadata, such as method call counts and received arguments, allowing state and behavioral inspection. A Mock is pre-configured with strict expectations and call verifications, driving interaction-based assertions where success depends on whether exact methods were invoked in sequence. A Fake is a fully functional, stateful implementation using algorithmic shortcuts—such as an in-memory HashMap repository—providing high fidelity without production infrastructure overhead.

## Practical walkthrough (English)

Implementing and contrasting Fakes, Stubs, Mocks, and Spies in Kotlin:
```kotlin
// 1. Production Contract
interface UserRepository {
    suspend fun getUser(id: String): User?
    suspend fun saveUser(user: User)
}

// 2. FAKE: Working in-memory implementation with internal state
class FakeUserRepository : UserRepository {
    private val memoryStore = mutableMapOf<String, User>()
    override suspend fun getUser(id: String): User? = memoryStore[id]
    override suspend fun saveUser(user: User) { memoryStore[user.id] = user }
}

// 3. STUB: Canned static responses without state tracking
class StubUserRepository(private val cannedUser: User) : UserRepository {
    override suspend fun getUser(id: String): User = cannedUser
    override suspend fun saveUser(user: User) { /* no-op */ }
}

// 4. SPY: Tracks invocations and inspects argument history
class SpyUserRepository(private val realRepo: UserRepository) : UserRepository by realRepo {
    var saveCallCount = 0
        private set
    var lastSavedUser: User? = null
        private set

    override suspend fun saveUser(user: User) {
        saveCallCount++
        lastSavedUser = user
        realRepo.saveUser(user)
    }
}

// 5. MOCK: Declarative expectation and verification using MockK
class UserUseCaseTest {
    @Test
    fun execute_verifiesStrictInteraction() = runTest {
        val mockRepo = mockk<UserRepository>()
        coEvery { mockRepo.saveUser(any()) } returns Unit

        val useCase = SaveUserUseCase(mockRepo)
        useCase(User("42", "Ali"))

        coVerify(exactly = 1) { mockRepo.saveUser(match { it.id == "42" }) }
    }
}
```

## Explanation in Arabic

قارن بين الـ Dummy، والـ Fake، والـ Stub، والـ Spy، والـ Mock، ومفهوم الـ Test Double العام وفقاً لمعايير مارتن فاولر؟

1. ما هو الـ Test Double؟
   - هو المفهوم المظلي الشامل لأي كائن بديل يُستخدم في بيئة الاختبار ليحل محل كائن حقيقي معقد أو يعتمد على موارد خارجية (مثل الشبكة أو قاعدة البيانات).

2. الأنواع الخمسة للـ Test Doubles:
   - **1. Dummy**: كائن يمرر فقط لملء المعاملات المطلوبة (Parameters) لتفادي أخطاء الـ NullPointerException، ولا يتم استخدام كوده أو استدعاء دواله إطلاقاً.
   - **2. Stub**: كائن يقدم إجابات معلبة وجاهزة مسبقاً (Canned Answers) لاستدعاءات محددة أثناء الاختبار (مثلاً: دالة `getUser()` تعيد دائماً مستخدماً ثابتاً `User("1")`).
   - **3. Spy**: كائن يسجل معلومات حول كيفية استدعائه (مثل: كم مرة تم استدعاؤه، وما هي المعاملات التي مُررت له) للتحقق منها لاحقاً.
   - **4. Mock**: كائن مبرمج مسبقاً بتوقعات صريحة (Expectations)؛ يتحقق تلقائياً من استدعاء دوال محددة بترتيب محدد عبر أدوات مثل MockK أو Mockito.
   - **5. Fake**: **البديل الأفضل والأكثر موثوقية**! كائن يملك تنفيذاً حقيقياً وشغالاً لمنطق العمل (Working Implementation)، ولكنه يعتمد على اختصار خفيف (مثل استبدال قاعدة بيانات SQLite بـ `MutableList` في الذاكرة).

## Practical walkthrough

المقارنة البرمجية بين كتابة Fake قوي وكتابة Mock هش باستخدام MockK:
```kotlin
// 1. Fake Repository (تطبيق شغال وقوي وخالٍ من الهشاشة في الذاكرة):
class FakeUserRepository : UserRepository {
    private val users = mutableMapOf<String, User>()

    override suspend fun getUser(id: String): User? = users[id]
    override suspend fun saveUser(user: User) {
        users[user.id] = user
    }
}

// 2. استخدام Mock عبر MockK (يتحقق من تفاصيل الاستدعاء ولكنه قد يكون هشاً عند إعادة الهيكلة):
class UserViewModelTest {
    @Test
    fun `loadUser calls repository exactly once with mock`() = runTest {
        val mockRepo = mockk<UserRepository>()
        coEvery { mockRepo.getUser("101") } returns User("101", "Mohamed")

        val viewModel = UserViewModel(mockRepo)
        viewModel.loadUser("101")

        // التحقق من أن الدالة تم استدعاؤها تحديداً مرة واحدة بنفس الـ ID:
        coVerify(exactly = 1) { mockRepo.getUser("101") }
    }
}
```

## Why it matters and how it works

Fakes model behavior and often support multiple tests; stubs provide canned responses; mocks verify interaction; spies observe real or wrapped behavior. Framework names can differ, so describe what the double does rather than rely on terminology alone.

## Worked example

For a ViewModel, an in-memory `PaymentsRepository` fake emits pending then approved. Assert `StateFlow` UI state. Mock an analytics port only when the event itself is the behavior under test; do not assert every incidental repository call.

## Trade-offs and decision criteria

Fakes can drift from production semantics, especially transactions/concurrency. Mocks are quick for rare failures but overuse couples tests to call order. Contract tests can check fake and real adapter behavior against the same expectations.

## Failure modes

A mock verifies `save()` called but the real Room implementation loses the write on rollback. Add integration coverage for persistence. A spy invokes real network unexpectedly; isolate side effects deliberately.

## Production perspective

Keep doubles local to test modules, specify failure/cancellation behavior, and review whether they preserve important contract rules. Use real database/HTTP adapters in focused integration tests.

## Interview answer — short

Test double is the universal umbrella term for any test substitute. A dummy is an unused placeholder to satisfy parameters. A stub provides canned data without logic. A spy records method calls and arguments for later inspection. A mock defines strict expectations on interactions, failing if expected calls do not occur. Finally, a fake is a working implementation with simplified state, such as an in-memory database, providing the highest fidelity and maintainability without external dependencies.

## Interview answer — structured

Mastering Gerard Meszaros' test double taxonomy allows senior developers to author resilient, expressive test suites while avoiding fragile mock traps.
Test double is the generic umbrella category that encompasses all test stand-ins.
A dummy is the simplest double; it exists purely to fill mandatory method parameters, such as passing a blank context or empty logger that is never exercised during the test.
A stub acts as an indirect input provider, returning predetermined, hardcoded results to specific method queries without maintaining internal state or validating how it was called.
A spy acts as an indirect output observer; it records telemetry about interactions—such as the number of times a method was called and the exact arguments passed—allowing assertions to inspect historical invocations after the execution finishes.
A mock is configured with pre-programmed behavioral expectations.
Rather than verifying resulting state, mock tests assert that specific methods were invoked with specific parameters, making the test focus heavily on execution mechanics.
A fake provides a fully operational, lightweight implementation of the production interface, such as maintaining an in-memory HashMap to simulate a database.
Senior engineers strongly favor fakes over mocks because fakes simulate real-world state transitions, do not break when internal class details are refactored, and execute without bytecode proxy overhead.

## Interview answer — deep senior

Under the hood, the choice between fakes and mocks dramatically impacts test runtime performance, refactoring safety, and internal compilation mechanics.
Mocking libraries like MockK and Mockito rely on dynamic bytecode generation.
On the JVM, they utilize ByteBuddy or Java dynamic proxies to subclass target interfaces and intercept method calls at runtime.
On Android ART devices, mocking is even more expensive, requiring dexmaker to dynamically patch Dalvik bytecode into the application's executable cache directory.
Every mock invocation traverses deep reflection interceptor call stacks to evaluate argument matchers and record invocation history.
Furthermore, mock-heavy testing often results in severe test brittleness; because assertions verify exact method names and call counts, harmless internal refactorings that preserve behavior can cause hundreds of mock tests to fail.
In contrast, a fake is compiled as standard Kotlin bytecode utilizing ordinary polymorphic dispatch.
An in-memory fake repository executes millions of operations per second using standard CPU cache lines and HashMap algorithms without reflection, proxy allocations, or dex patching.
Fakes enable state-based verification: the test exercises business actions and asserts the resulting domain state, leaving the internal collaboration details completely unconstrained.
Senior engineers maintain shared fake implementations alongside production code in dedicated testing modules, ensuring that contract updates immediately propagate to all unit tests across the engineering organization.

## How to answer in the interview

- **Why:** doubles keep tests deterministic without coupling them to every implementation call.
- **How:** name stub, fake, mock and spy, then choose a fake repository for state behavior.
- **Trade-off:** interaction checks are precise but can be brittle.
- **Failure case:** a fake map hides transaction semantics.
- **Production solution:** pair behavior tests with a real-boundary integration test.

## Deep-dive talking points

Prompt for five roles, outcome versus interaction, fake drift and real-adapter verification.

## Follow-up questions

- **Interviewer:** "Why does Google's Android testing guidance recommend Fakes over Mocks for Repositories?"
  **Answer:** "Fakes provide realistic stateful behavior, survive internal code refactoring without breaking tests, and can be reused across hundreds of tests without brittle mock setup."

- **Interviewer:** "What is the risk of using relaxed mocks in MockK (relaxed = true)?"
  **Answer:** "Relaxed mocks return default dummy values (0, empty string, null) for unmocked calls, which can mask missing setup errors and hide broken data flow."

## Self-check rubric

Distinguish the umbrella term test double from stubbed answers, behavior-verifying mocks, stateful fakes and observation spies. Choose a fake repository for a ViewModel state test and explain when verifying a collaborator call is actually the requirement.

## References and reviewed-on date

- [Android test doubles](https://developer.android.com/training/testing/fundamentals/test-doubles) — official definitions and guidance.
- [Mockito documentation](https://site.mockito.org/) — mock interaction behavior.

Technically reviewed against primary documentation on 2026-10-13.
