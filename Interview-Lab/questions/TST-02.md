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

Test double is the umbrella term. Dummies fill parameter slots without being used. Stubs return canned responses. Spies record interactions for verification. Mocks define pre-programmed expectations verified on assertions. Fakes provide lightweight, working in-memory implementations (like an in-memory list repository).

## Interview answer — structured

Understanding test doubles follows the classic Martin Fowler taxonomy.

First, **Dummy**. Next, objects passed around simply to satisfy method signatures (e.g. An empty constructor parameter), never actually interrogated or invoked.
**Stub**. Provides canned responses to method calls during a test (e.g. `every { api.getUser() } returns sampleUser`). Stubs do not verify interaction behavior; they only supply required data state.
**Spy**. Wraps a real or stubbed instance to record telemetry: capturing argument parameters, invocation counts, and order of calls for post-execution assertions.
**Mock**. Objects pre-programmed with expected interaction behavior and verified at assertion time (`verify { service.trackEvent("purchase") }`). Mocks focus on behavior verification rather than state verification.
**Fake**. Finally, objects that have working business logic, but take shortcuts unsuitable for production (e.g., an in-memory `FakeUserRepository` backed by a `ConcurrentHashMap` rather than SQLite).


## Interview answer — deep senior

From a software maintainability and Google engineering practices perspective, Fakes are heavily favored over Mocks.

First, with The Fragility of Over-Mocking, tests relying heavily on MockK/Mockito verify implementation details (which methods were called and how many times) rather than observable behavior and state. When an engineer refactors internal repository code to batch calls or use caching, mocked tests break instantly despite correct user behavior. Next, fakes Enable Realistic Multi-Feature Tests is a well-designed `FakeCartRepository` behaves like the real repository: saving items, updating quantities, and emitting reactive state flows. Multiple ViewModels and tests can share the same fake across integration suites with zero mocking boilerplate.
Finally, with When Mocks are Justified, use mocks sparingly: primarily for un-fakeable external boundaries where asserting exact side effects is the direct goal (e.g. Asserting that a payment SDK's `initiatePayment()` or analytics tracker was triggered exactly once).


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
