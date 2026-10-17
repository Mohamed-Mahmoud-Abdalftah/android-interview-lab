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

## Concept and technical explanation

Composition over inheritance is a foundational object-oriented design principle asserting that systems should achieve code reuse, polymorphism, and behavioral extension by assembling independent components through 'has-a' reference relationships rather than constructing rigid class hierarchies through 'is-a' inheritance trees. In Android engineering, excessive inheritance results in the notorious Fragile Base Class problem, monolithic BaseActivity and BaseFragment anti-patterns, inflexible compile-time coupling, and namespace pollution. Favoring composition enables dynamic runtime behavioral swapping, clean lifecycle observers, pure JVM testability, and forms the core foundational paradigm of modern Jetpack Compose.

## Practical walkthrough (English)

Refactoring a bloated BaseActivity inheritance tree into decoupled composition:
```kotlin
// BAD ANTI-PATTERN: Bloated BaseActivity (Fragile base class, tight coupling, hard to test)
open class BaseActivity : AppCompatActivity() {
    fun trackAnalytics(event: String) { /* Concrete mixpanel logic */ }
    fun showLoadingDialog() { /* Dialog logic */ }
    fun checkLocationPermission() { /* Activity permission requests */ }
    // Every child activity inherits all 50 methods whether it needs them or not!
}
class CheckoutActivity : BaseActivity() { /* Inherits massive baggage */ }

// ARCHITECTURAL BEST PRACTICE: Composition via dedicated delegates & lifecycle observers
class AnalyticsTracker @Inject constructor() {
    fun trackScreen(screenName: String) { /* Clean isolated analytics */ }
}

class LocationPermissionDelegate(private val activity: ComponentActivity) {
    // Encapsulates permission contracts independently
    fun requestLocation(onGranted: () -> Unit) { /* ... */ }
}

// Clean Activity: Composes only the capabilities it actually requires
@AndroidEntryPoint
class CleanCheckoutActivity : AppCompatActivity() {
    @Inject lateinit var analytics: AnalyticsTracker
    private val locationDelegate by lazy { LocationPermissionDelegate(this) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        analytics.trackScreen("Checkout")
    }
}
```

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

Composition over inheritance favors assembling components using 'has-a' relationships over building deep 'is-a' inheritance trees. In Android, inheritance creates bloated BaseActivity anti-patterns where every screen inherits irrelevant analytics, dialog, and permission methods. Composition replaces this by injecting independent, reusable helpers and lifecycle observers, avoiding fragile base class bugs and providing the foundational architectural model for Jetpack Compose.

## Interview answer — structured

The principle of favoring composition over inheritance resolves the architectural fragility inherent in deep class inheritance trees.
Class inheritance creates white-box code reuse where child classes are tightly coupled to the internal implementation mechanics and protected fields of their parents. In Android development, this anti-pattern manifests most visibly in bloated BaseActivity and BaseFragment hierarchies. Over years of development, teams dump analytics tracking, toolbar setup, loading spinners, network retry dialogs, and permission handling into a monolithic base class. Every child screen inherits dozens of methods and lifecycle hooks it does not need, creating namespace collisions, accidental method override bugs, and untestable code.
Composition solves this by treating capabilities as discrete, swappable components assembled via 'has-a' references.
Instead of an Activity inheriting from a base class to gain analytics capabilities, it has an AnalyticsTracker injected into it. Instead of inheriting permission mechanics, it delegates to a LocationPermissionHelper that observes the Activity's Lifecycle.
This approach eliminates the fragile base class problem, makes testing straightforward by allowing individual delegates to be mocked or faked on the JVM, and allows components to be combined flexibly without rigid parent-child hierarchies.

## Interview answer — deep senior

Under the hood, composition fundamentally transforms memory layout, runtime dispatch, and evolutionary adaptability in Android applications.
Class inheritance fixes behavior statically at compile time: once class CheckoutActivity extends BaseActivity, its class hierarchy, v-table offsets, and superclass constructor chains are permanently baked into DEX bytecode. If the base class constructor allocates expensive resources, every single derived Activity pays that heap and startup latency penalty, even for lightweight splash or deep-link routing screens.
With composition, capabilities are allocated lazily and conditionally. A screen only instantiates delegates it actively uses, keeping the runtime heap footprint minimal.
Furthermore, Kotlin provides native language ergonomics for composition through interface delegation using the by keyword (class SecureStorage(inner: Storage) : Storage by inner). This delivers the syntax convenience of inheritance with the structural safety of composition.
Most importantly, composition is the defining paradigm shift behind Jetpack Compose. In the legacy View framework, every UI element extended the monolithic android.view.View class (which contains over 30,000 lines of code and hundreds of fields). Jetpack Compose completely abandons this inheritance model. A Compose UI tree is constructed purely through function composition, passing modifiers and state holders as parameters, ensuring that UI components remain lightweight, decoupled, and trivially reusable across multiple platforms.

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
