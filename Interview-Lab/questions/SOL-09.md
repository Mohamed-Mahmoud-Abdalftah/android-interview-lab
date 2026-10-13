---
id: "SOL-09"
question: "What is composition over inheritance?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "A"
phase: 2
priority: "P1"
order: 180
editorial_status: "reviewed"
---

# SOL-09

## Original interview question

What is composition over inheritance?

## What the interviewer evaluates

Explain flexible behavior assembly without fragile base-class coupling, while recognizing valid inheritance.

## Explanation in Arabic

ما هو مبدأ تفضيل التركيب على الوراثة (Composition over Inheritance) ولماذا هو أساسي في Android الحديث؟

1. ما هو الفرق بين التركيب (Composition) والوراثة (Inheritance)؟
   - **الوراثة (Inheritance - "is-a")**: كلاس فرعي يرث كل شيء من كلاس أب (`class ProfileActivity : BaseActivity()`).
     * المشاكل القاتلة: **الاقتران الشديد (Tight Coupling)** و **هشاشة الكلاس الأساسي (Fragile Base Class)**؛ أي تعديل في الكلاس الأساسي قد يكسر عشرات الشاشات الفرعية بصمت، ولا يمكن وراثة أكثر من كلاس واحد في Kotlin/Java!
   - **التركيب (Composition - "has-a")**: تجميع كائنات صغيرة مستقلة تؤدي وظائف محددة بداخل الكلاس (`class ProfileScreen(val toolbarHandler: ToolbarHandler, val analytics: AnalyticsTracker)`).
     * المزايا: مرونة تامة، إمكانية تبديل السلوكيات في وقت التشغيل، سهولة الاختبار الفردي لكل مكون، وتجنب شجرة الوراثة المعقدة.

2. كيف يظهر هذا المبدأ في Jetpack Compose؟
   - Jetpack Compose مبني بنسبة **100% على التركيب (Composition)**!
   - لا يوجد في Compose كلاس يرث من كلاس؛ بل شاشة `Scaffold` تركّب بداخلها `TopAppBar` و `FloatingActionButton` و `Content` كدوال مستقلة تماماً.

## Practical walkthrough

استبدال الوراثة الهشة بكائنات مركبة عبر تفويض كوتلن (Kotlin Delegation):
```kotlin
// ❌ وراثة هشة: شجرة كلاسات Base عميقة يصعب تعديلها واختبارها:
open class BaseActivity : AppCompatActivity() { /* 500 سطر للتحليلات وشريط الأدوات */ }
open class AuthenticatedBaseActivity : BaseActivity() { /* 300 سطر للتحقق من الجلسة */ }
class OrdersActivity : AuthenticatedBaseActivity() { /* مقيدة بشجرة وراثة صلبة! */ }

// ✅ التركيب (Composition): سلوكيات مستقلة تُركب حسب الحاجة عبر Kotlin by:
interface SessionObserver {
    fun registerSessionTimeout(activity: Activity)
}
class SessionObserverImpl : SessionObserver { ... }

interface AnalyticsLogger {
    fun logScreen(name: String)
}
class FirebaseAnalyticsLogger : AnalyticsLogger { ... }

// تركيب السلوكيات في الشاشة دون وراثة هشة:
class OrdersActivity(
    private val session: SessionObserver = SessionObserverImpl(),
    private val analytics: AnalyticsLogger = FirebaseAnalyticsLogger()
) : AppCompatActivity(), SessionObserver by session, AnalyticsLogger by analytics {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate()
        registerSessionTimeout(this)
        logScreen("OrdersScreen")
    }
}
```

## Why it matters and how it works

Composition localizes optional behavior and makes dependencies visible. Inheritance reuses implementation and establishes subtype obligations. Prefer composition when clients need varying capabilities rather than one fixed base contract.

## Worked example

Conceptual design: `class CheckoutCoordinator(private val analytics: Analytics, private val navigator: Navigator)` composes two services. A screen with no toolbar simply omits `ToolbarController`; it does not inherit `BaseFragment.setupToolbar()` and throw.

## Trade-offs and decision criteria

Composition requires wiring and can introduce indirection. Inheritance can be concise for a stable genuine subtype hierarchy. Kotlin classes are final by default, nudging deliberate extension. Choose by behavioral substitution, not blanket style.

## Failure modes

A giant BaseFragment holds Activity context, toolbar, analytics and payment SDK state; one child does not support toolbar and overrides it to throw. This couples lifecycles and violates the base promise. Extract capabilities and scope them to owners.

## Production perspective

An app uses small injected collaborators for analytics and navigation, with lifecycle-aware registration. Tests replace each capability independently; feature fragments share only the framework base class they truly need.

## Interview answer — short

Composition over inheritance favors assembling components with 'has-a' relationships over rigid 'is-a' inheritance trees. In Android, it eliminates bloated `BaseActivity` anti-patterns, enables runtime behavioral flexibility, avoids the fragile base class problem, and is the foundational architecture of Jetpack Compose.

## Interview answer — structured

The principle of 'Composition over Inheritance' advocates that classes should achieve polymorphic reuse by containing instances of other classes ('has-a') rather than inheriting state and behavior from a superclass ('is-a').

1. **The Fragility of Inheritance**:
   - Inheritance creates the tightest possible compile-time coupling: changes to private or protected implementations in a superclass ripple unpredictably across derived subclasses (the *Fragile Base Class problem*).
   - Subclasses inherit irrelevant or unwanted behaviors (violating LSP).
   - Single inheritance in Kotlin/Java prevents combining multiple orthogonal features (e.g. an Activity cannot inherit from both `BaseCameraActivity` and `BaseBillingActivity`).

2. **The Power of Composition**:
   - Components encapsulate isolated concerns (`AnalyticsHelper`, `SessionTracker`, `ToolbarCoordinator`).
   - Components can be dynamically plugged in, swapped, or mocked in unit tests.
   - Promotes high cohesion and clean unit testability.

Jetpack Compose is the ultimate manifestation of this principle: Compose completely abandons the 15-year-old `android.view.View` inheritance tree in favor of pure, composable function graphs.

## Interview answer — deep senior

Kotlin offers first-class language support for composition via **Class Delegation (`by`)**. By declaring `class MyActivity : AppCompatActivity(), AnalyticsManager by analyticsManager`, Kotlin generates forwarding bytecode calls under the hood. This delivers the syntactic convenience of inheritance while preserving the architectural purity and loose coupling of composition.

In Android Jetpack, `LifecycleObserver` and `LifecycleEventObserver` represent the official migration from inheritance to composition: instead of overriding `onStart()` in a `BaseActivity`, self-contained components observe `lifecycle.addObserver(myComponent)`, managing their own cleanup automatically.

## How to answer in the interview

- **Why:** Give BaseFragment failure.
- **How:** show collaborator composition.
- **Trade-offs:** acknowledge wiring cost.
- **Failure cases:** mention empty overrides and lifecycle leaks.
- **Production solutions:** finish with owner-scoped collaborators and recreation tests..

## Deep-dive talking points

Compare BaseFragment hooks with injected capabilities; discuss LSP, lifecycle ownership and Kotlin final-by-default classes.

## Follow-up questions

- **Interviewer:** "When is inheritance still acceptable?"
  **Answer:** "When there is a genuine, immutable 'is-a' relationship where the subclass is a true specialized extension of the parent and obeys LSP without exception, or when extending third-party framework classes like `ViewModel` or `Fragment`."

- **Interviewer:** "How does `LifecycleObserver` replace BaseActivity callbacks?"
  **Answer:** "Instead of subclasses calling `super.onStart()`, a component implements `DefaultLifecycleObserver` and registers itself with the Activity's lifecycle, executing setup and teardown independently."

## Self-check rubric

Redesign one bloated base class with two collaborators and state one valid inheritance case.

## References and reviewed-on date

- [Kotlin inheritance](https://kotlinlang.org/docs/inheritance.html) — explicit inheritance mechanics.
- [Kotlin delegation](https://kotlinlang.org/docs/delegation.html) — composition through forwarding.

Technically reviewed against primary documentation on 2026-10-13.
