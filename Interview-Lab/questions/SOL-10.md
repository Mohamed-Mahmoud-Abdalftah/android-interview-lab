---
id: "SOL-10"
question: "A BaseFragment requires setupToolbar() but some screens have no toolbar. When does this violate LSP?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "B"
phase: 2
priority: "P1"
order: 181
editorial_status: "reviewed"
---

# SOL-10

## Original interview question

A BaseFragment requires setupToolbar() but some screens have no toolbar. When does this violate LSP?

## What the interviewer evaluates

Identify when a mandatory base hook creates behavioral substitution failure and offer an incremental replacement.

## Concept and technical explanation

Mandating a setupToolbar() method in an abstract or open BaseFragment violates the Liskov Substitution Principle (LSP) whenever derived fragments that do not possess a toolbar are forced to override the method by throwing UnsupportedOperationException, returning unexpected nulls, or implementing a silent no-op that breaks base class invariants or lifecycle expectations. When a base class establishes a behavioral contract, any host orchestrator (such as a Navigation component, parent Activity, or test harness) treating derived fragments polymorphically assumes that calling setupToolbar() performs valid configuration. If a subclass cannot fulfill this contract legitimately, it cannot be substituted safely for its base type, violating LSP.

## Practical walkthrough (English)

Refactoring an LSP-violating BaseFragment using optional capability interfaces:
```kotlin
// BAD ANTI-PATTERN: Violates LSP (Forced override throws exception or silent no-ops breaking contracts)
abstract class BadBaseFragment : Fragment() {
    abstract fun setupToolbar(): Toolbar // Contract implies EVERY screen has a valid Toolbar!
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        val toolbar = setupToolbar()
        (activity as? AppCompatActivity)?.setSupportActionBar(toolbar)
    }
}

class FullscreenMediaFragment : BadBaseFragment() {
    override fun setupToolbar(): Toolbar {
        // BLATANT LSP VIOLATION: Subclass cannot fulfill contract and crashes the app!
        throw UnsupportedOperationException("Fullscreen screen has no toolbar!")
    }
}

// ARCHITECTURAL BEST PRACTICE: Segregated optional capability contract adhering to LSP
interface ToolbarHost {
    fun configureToolbar(toolbar: Toolbar)
}

// Base Fragment manages ONLY genuine universal concerns (or eliminate BaseFragment entirely!)
abstract class CleanBaseFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // Check capability polymorphically without forcing subclasses to fake implementations
        if (this is ToolbarHost) {
            view.findViewById<Toolbar?>(R.id.toolbar)?.let { configureToolbar(it) }
        }
    }
}

// Screens with a toolbar explicitly opt into the contract
class HomeFragment : CleanBaseFragment(), ToolbarHost {
    override fun configureToolbar(toolbar: Toolbar) {
        toolbar.title = "Home"
    }
}

// Fullscreen screen simply does NOT implement ToolbarHost (100% LSP compliant!)
class FullscreenFragment : CleanBaseFragment() { /* No toolbar baggage! */ }
```

## Explanation in Arabic

عندما يفرض كلاس `BaseFragment` تنفيذ دالة `setupToolbar()` ولكن بعض الشاشات ليس بها Toolbar: متى ينتهك هذا مبدأ LSP؟ وكيف يُعالج؟

1. متى وكيف ينتهك هذا مبدأ لسكوف (LSP Violation)؟
   - ينتهك LSP فوراً عندما يتوقع الكلاس الأساسي (أو مستدعي الكود) أن الدالة `setupToolbar()` ستقوم بتهيئة شريط أدوات صالح، ولكن الكلاس الفرعي:
     * يرمي استثناء: `throw UnsupportedOperationException("No toolbar")` مما يسبب Crash للمستخدم.
     * أو يترك الدالة فارغة كـ No-op، فيقوم الكود الخارجي بالتعامل مع Toolbar غير موجود (NullPointer أو سلوك خفي مكسور).
   - النتيجة: لا يمكن استبدال `BaseFragment` بـ `NoToolbarFragment` بأمان دون حدوث مفاجآت وسلوكيات مكسورة.

2. العلاج المعماري الجذري:
   - **إزالة الدالة من الـ BaseClass فوراً**: الكلاس الأساسي يجب ألا يفرض إلا السلوكيات المشتركة بين 100% من الشاشات.
   - **إنشاء واجهة اختيارية (Marker/Capability Interface)**: `interface HasToolbar { fun getToolbar(): Toolbar }`.
   - أو الأفضل: استخدام **Delegate مستقل** يتم استدعاؤه فقط داخل الشاشات التي تحتاج لشريط أدوات.

## Practical walkthrough

معالجة انتهاك LSP في شاشات الـ Fragments:
```kotlin
// ❌ انتهاك LSP: BaseFragment يفرض Toolbar على شاشات لا تحتاجه (كالشاشات المنبثقة والشاشات الكاملة):
abstract class LeakyBaseFragment : Fragment() {
    abstract fun setupToolbar(): Toolbar // فرض إلزامي!
}

class FullscreenPlayerFragment : LeakyBaseFragment() {
    override fun setupToolbar(): Toolbar {
        // 💥 يكسر LSP: يرمي استثناء أو يعيد null بطريقة غير متوقعة:
        throw UnsupportedOperationException("No toolbar in video player")
    }
}

// ✅ الحل المعماري المتوافق مع LSP: فصل القدرات في Interface أو Delegate:
abstract class SafeBaseFragment : Fragment() {
    // يحتوي فقط على السلوكيات العامة المشتركة بين 100% من الشاشات (مثل التحليلات أو الربط الأساسي)
}

// واجهة خاصة بالشاشات التي تمتلك Toolbar فقط:
interface ToolbarProvider {
    fun configureToolbar(toolbar: Toolbar)
}

class CatalogFragment : SafeBaseFragment(), ToolbarProvider {
    override fun configureToolbar(toolbar: Toolbar) { /* إعداد Toolbar للشاشة */ }
}

class SafePlayerFragment : SafeBaseFragment() {
    // لا ينفذ ToolbarProvider، ولا يكسر أي عقود!
}
```

## Why it matters and how it works

LSP depends on the base contract, not merely the existence of a no-op. A subclass must honor valid base expectations. Forcing unsupported behavior suggests the abstraction is too broad; composition or a narrower interface clarifies capability.

## Worked example

Conceptual Kotlin:
```kotlin
interface ToolbarHost { fun configureToolbar(title: String) }
class CheckoutHeader(private val host: ToolbarHost) {
    fun show() = host.configureToolbar("Checkout")
}
```
A full-screen camera Fragment does not implement `ToolbarHost` and need not pretend to support it.

## Trade-offs and decision criteria

A default no-op can be acceptable if optional behavior is explicit and callers do not rely on it. A capability interface adds wiring but prevents invalid base assumptions. Avoid adding an interface if a simple local helper suffices.

## Failure modes

A subclass throws `UnsupportedOperationException` from `setupToolbar`, so a base lifecycle callback crashes on that screen. Replace mandatory hook and migrate toolbar screens behind an explicit capability; test both toolbar and no-toolbar navigation.

## Production perspective

A media app has camera and library Fragments. Only library screens compose a toolbar controller; camera screen stays immersive. Shared analytics remains a separate lifecycle-aware collaborator rather than a BaseFragment field.

## Interview answer — short

Forcing setupToolbar() inside BaseFragment violates the Liskov Substitution Principle when derived screens lack a toolbar and must throw UnsupportedOperationException, return null, or provide a silent no-op that breaks caller expectations. If callers polymorphically invoke setupToolbar() expecting a configured toolbar, the program crashes or corrupts layout state. The fix is removing setupToolbar() from the base class and moving it to an optional capability interface like ToolbarHost.

## Interview answer — structured

Requiring all fragments to implement setupToolbar() exposes a textbook violation of the Liskov Substitution Principle arising from speculative base class design.
When a base class declares abstract fun setupToolbar(): Toolbar or relies on an open method, it establishes a formal contract: every child fragment is guaranteed to have a functional Toolbar and can configure it during view creation.
This violates LSP the moment a screen without a toolbar is introduced, such as a full-screen video player, an onboarding carousel, or a splash screen.
If the developer overrides setupToolbar() to throw UnsupportedOperationException, any polymorphic caller invoking the method triggers a fatal runtime crash, blatantly violating substitutability.
If the developer returns null where a non-null Toolbar was expected, the parent Activity or base class triggers a NullPointerException.
Even if the method is designed to return a nullable Toolbar and the child returns null, or if the method has an empty body, it violates LSP if the base class assumes that a toolbar is present to wire navigation icons, menu inflation, or title updates.
To resolve this cleanly, toolbar configuration should be removed from BaseFragment entirely. Instead, define an optional ToolbarHost capability interface or delegate toolbar configuration to individual screens, ensuring every subclass satisfies its contracts completely.

## Interview answer — deep senior

Under the hood, this scenario illustrates how inheritance hierarchies conflate shared framework lifecycles with heterogeneous UI capabilities.
A Fragment is a framework lifecycle controller, whereas a Toolbar is an optional presentation widget. Forcing a widget-specific contract into a lifecycle controller's base class creates tight, unworkable coupling.
In enterprise Android development, when BaseFragment invokes setupToolbar() inside onViewCreated(), it assumes the existence of view hierarchy elements before derived classes have even bound their state machines. When a child fragment provides a no-op or returns null, it often causes parent Activity action bar state corruption, where the previous screen's toolbar remains attached to the Activity's window decor, leading to stale menu items and broken back-arrow navigation.
Senior architects resolve this by moving away from inheritance entirely toward composition and capability interfaces.
If using Fragments, the screen implements an optional interface: interface ToolbarProvider { val toolbarResId: Int }. The Activity or a dedicated NavigationListener interrogates the current destination: if (currentFragment is ToolbarProvider), it configures the Action Bar; otherwise, it collapses or hides it.
In modern Jetpack Compose, this entire category of bugs is eradicated by design. In Compose, top app bars are standard composable components declared inside a screen's Scaffold(topBar = { TopAppBar(...) }). Screens that do not need a toolbar simply omit the topBar parameter, achieving complete structural independence without fragile base class inheritance.

## How to answer in the interview

- **Why:** State the promised base behavior.
- **How:** explain substitution at caller site.
- **Trade-offs:** mention optional-contract nuance.
- **Failure cases:** show throw/no-op failure.
- **Production solutions:** propose explicit capability and caller tests..

## Deep-dive talking points

State base contract precisely, distinguish no-op from throw, and outline a safe capability extraction.

## Follow-up questions

- **Interviewer:** "Why is eliminating `BaseFragment` completely considered best practice today?"
  **Answer:** "Base classes create rigid inheritance hierarchies, hide dependencies, cause LSP violations, and slow down build times. Composition via delegates and Compose UI provides far greater flexibility and testability."

- **Interviewer:** "How does Jetpack Compose solve the optional toolbar problem?"
  **Answer:** "Compose's `Scaffold` composable accepts an optional `topBar: @Composable () -> Unit = {}` parameter. If a screen has no toolbar, you simply omit the parameter without subclassing or overriding anything."

## Self-check rubric

Explain the contract condition for violation, give a counterexample where optional no-op is legal, and propose a refactor.

## References and reviewed-on date

- [Kotlin inheritance](https://kotlinlang.org/docs/inheritance.html) — override behavior.
- [Liskov and Wing, A Behavioral Notion of Subtyping](https://www.cs.columbia.edu/~wing/publications/LiskovWing94.pdf) — substitutability.

Technically reviewed against primary documentation on 2026-10-13.
