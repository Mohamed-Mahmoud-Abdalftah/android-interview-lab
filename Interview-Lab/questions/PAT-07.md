---
id: "PAT-07"
question: "What does Dependency Injection as a pattern accomplish?"
topic: "Design Patterns"
code: "PAT"
group: "A"
phase: 2
priority: "P1"
order: 198
editorial_status: "reviewed"
---

# PAT-07

## Original interview question

What does Dependency Injection as a pattern accomplish?

## What the interviewer evaluates

Explain external provisioning of dependencies, graph composition, test substitution and lifecycle scope.

## Explanation in Arabic

ما الذي يحققه نمط حقن التبعيات (Dependency Injection - DI كنمط تصميم) في تطبيقات Android؟

1. ما هي المشكلة بدون حقن التبعيات؟
   - عندما يقوم الكلاس بإنشاء التبعيات التي يحتاجها بنفسه داخل جسمه (`val api = Retrofit.Builder()...build()` أو `val repo = UserRepositoryImpl()`):
   - **اقتران شديد (Hard Coupling)**: الكلاس ارتهن بكلاس ملموس محدد، ولا يمكن تبديله.
   - **استحالة الـ Unit Testing**: لا يمكنك اختبار الكلاس بشكل معزول على الـ JVM، لأنك لا تستطيع استبدال `api` أو `db` بـ Fake أو Mock.
   - **فوضى إدارة دورات الحياة (Lifecycle Chaos)**: كل كلاس ينشئ نسخته الخاصة، مما يكرر كائنات ثقيلة في الذاكرة.

2. ما الذي يحققه نمط الـ Dependency Injection (DI)؟
   - **فصل الإنشاء عن الاستخدام (Separation of Creation from Consumption)**: الكلاس يعلن فقط عما يحتاجه في الـ Constructor (`Constructor Injection`)، ويتولى مجمع خارجي (DI Container مثل Hilt/Koin) تزويده بها.
   - **سهولة الاختبار الخارق (Testability)**: في الـ Unit Test، تمرر ببساطة `FakeUserRepository()` في الـ Constructor مباشرة دون الحاجة لأي مكتبات أو أطر عمل.
   - **إدارة مركزية للـ Scopes ودورات الحياة**: ضمان مشاركة نسخة واحدة من كائن الـ Singleton وتحرير الكائنات المرتبطة بنشاط محدد عند انتهائه.

## Practical walkthrough

المقارنة بين كلاس ينشئ تبعياته بنفسه وكلاس يعتمد على الـ Dependency Injection:
```kotlin
// ❌ بدون DI: كلاس ينشئ تبعياته بنفسه؛ اقتران صلب واستحالة للاختبار:
class BadOrderViewModel : ViewModel() {
    // إنشاء مباشر يربط الـ ViewModel بالسيرفر وقاعدة البيانات الحقيقية:
    private val repository = OrderRepositoryImpl(RetrofitClient.api, AppDatabase.getDao())
    // لا يمكن اختبار هذا الـ ViewModel على الـ JVM دون تشغيل قاعدة بيانات وشبكة حقيقية!
}

// ✅ مع Dependency Injection (Constructor Injection):
@HiltViewModel
class GoodOrderViewModel @Inject constructor(
    private val repository: OrderRepository // التبعية تُمرر من الخارج
) : ViewModel() {
    val orders = repository.observeOrders()
}

// في الـ Unit Test: اختبار فوري في 2 مللي ثانية بتمرير Fake:
@Test
fun testOrderViewModel() {
    val fakeRepo = FakeOrderRepository()
    val viewModel = GoodOrderViewModel(fakeRepo) // تمرير التبعية يدوياً بسهولة فائقة!
    assertNotNull(viewModel.orders)
}
```

## Why it matters and how it works

DI separates construction from use. It makes dependencies visible, enables fakes and centralizes scope decisions. A container is optional; the pattern can be implemented manually. It does not select good abstraction boundaries automatically.

## Worked example

JVM illustration:
```kotlin
interface Clock { fun nowMillis(): Long }
class ExpiryPolicy(private val clock: Clock) {
    fun expired(deadline: Long) = clock.nowMillis() >= deadline
}
```
Production composition supplies a system clock; tests supply a fixed clock. No Android dependency is needed for policy tests.

## Trade-offs and decision criteria

Manual DI is transparent for small graphs; Hilt reduces repetitive wiring as a graph grows but adds build tooling and scope complexity. Service locator hides dependencies and makes tests order-dependent. Avoid interfaces for every pure helper.

## Failure modes

A singleton-scoped network service stores an Activity passed through a constructor, leaking it across recreation. Use application context only where appropriate and inject lifecycle-bound collaborators into matching scopes.

## Production perspective

An Android app wires repositories, API clients and ViewModels through Hilt, while domain unit tests construct policies directly with fake clocks/repositories. Scope tests verify no Activity leaks.

## Interview answer — short

Dependency Injection as a pattern decouples object consumption from object creation by passing dependencies from the outside (typically via constructor injection). It enables effortless JVM unit testing via Fakes, centralizes lifecycle and scope management, and enforces the Inversion of Control principle.

## Interview answer — structured

Dependency Injection (DI) is a specialized form of the Inversion of Control (IoC) pattern where an object receives its dependencies from an external assembler rather than instantiating them internally.

1. **Core Problem Solved**:
   - Without DI, a class hardcodes its dependencies (`val api = RetrofitInstance.create()`). The class becomes tightly coupled to concrete implementations, lifecycle configuration, and infrastructure environments.
   - Unit testing becomes impossible because collaborators cannot be substituted with test doubles.

2. **What DI Accomplishes**:
   - **Separation of Creation from Use**: Classes declare *what* collaborators they need in their constructor; an external container (Hilt, Koin, or manual DI) decides *how and when* to instantiate them.
   - **Frictionless Unit Testing**: In JVM tests, developers instantiate classes directly, passing fast in-memory Fakes without bootstrapping DI containers or Android frameworks.
   - **Centralized Scope & Lifecycle Management**: Tools like Hilt manage object scopes (`@Singleton`, `@ViewModelScoped`, `@ActivityScoped`), eliminating manual memory retention and teardown boilerplate.

## Interview answer — deep senior

A vital architectural realization is that **Dependency Injection is a pattern, not a library**. You can practice clean DI using **Pure / Manual Constructor Injection** without Dagger, Hilt, or Koin. Frameworks simply automate the tedious compile-time graph resolution and factory generation.

There are three types of Dependency Injection:
1. **Constructor Injection**: The gold standard in modern Android. Guarantees that dependencies are non-null, immutable (`val`), and explicit upon creation.
2. **Method / Parameter Injection**: Passing a collaborator into a specific function (e.g. `useCase.execute(dispatcher)`).
3. **Field Injection**: Necessary in Android only when the system instantiates classes via reflection (e.g. Activities and Services in `@AndroidEntryPoint`).

## How to answer in the interview

- **Why:** Explicit dependencies improve ownership and deterministic tests.
- **How:** Inject `Clock` and repository through constructors or a scoped graph.
- **Trade-off:** Manual DI is fine when graph complexity is small.
- **Failure case:** App-scoped object retains Activity or stale session data.
- **Production solution:** Test fake time and account-scope teardown, not just construction.

## Deep-dive talking points

Compare manual composition with Hilt, constructor visibility, service locator and scope ownership.

## Follow-up questions

- **Interviewer:** "Why is Constructor Injection preferred over Field Injection?"
  **Answer:** "Constructor injection ensures dependencies are required, immutable (`val`), and fully initialized at construction time, preventing temporal coupling and allowing classes to be instantiated cleanly in unit tests without reflection."

- **Interviewer:** "What is the difference between Service Locator and Dependency Injection?"
  **Answer:** "A Service Locator queries an external registry internally (`locator.get<Repo>()`), hiding dependencies inside the class. DI inverts control by explicitly passing dependencies into the constructor from the outside."

## Self-check rubric

Show one constructor-injected dependency, a fake test, and a scope mistake DI does not prevent.

## References and reviewed-on date

- [Android dependency injection](https://developer.android.com/training/dependency-injection) — DI on Android.
- [Kotlin classes](https://kotlinlang.org/docs/classes.html) — constructor mechanics.

Technically reviewed against primary documentation on 2026-10-13.
