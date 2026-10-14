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

It violates LSP when the caller expects a functional toolbar contract, but a subclass throws `UnsupportedOperationException`, returns null, or no-ops, breaking behavioral expectations. Fix it by removing `setupToolbar()` from `BaseFragment` and moving it to an optional `ToolbarProvider` capability interface or composable delegate.

## Interview answer — structured

A `BaseFragment` enforcing an abstract `setupToolbar()` violates the Liskov Substitution Principle (LSP) whenever a subclass cannot fulfill that contract meaningfully.

Under LSP, any client holding a reference to `BaseFragment` should be able to invoke `setupToolbar()` with the guarantee that a toolbar exists, has been configured, and conforms to lifecycle invariants. When a fullscreen video player, bottom sheet, or modal dialog subclasses `BaseFragment`, it has no toolbar. If the developer.

First, with Throws `UnsupportedOperationException, it breaks program execution at runtime. Finally, with Returns null or executes an empty no-op, it breaks postconditions, leading to silent bugs or subsequent `NullPointerException`s if the host Activity queries the fragment's toolbar.

**The Architectural Remedy**.

First, remove `setupToolbar()` entirely from `BaseFragment`. A base class must define *only* invariants that apply to 100% of all derived classes. Next, extract toolbar capability into an optional interface: `interface ToolbarHost { fun getToolbar(): Toolbar }`.
Finally, the hosting Activity inspects `if (fragment is ToolbarHost)` before configuring navigation bars, preserving substitution safety.


## Interview answer — deep senior

This scenario exposes the fundamental flaw of **inheritance-driven architecture**. Base classes tend to accumulate 'feature creep' over years: one developer adds toolbar logic, another adds swipe-to-refresh, a third adds FAB handling, until `BaseFragment` is 1,200 lines long and every new screen must fight against inherited assumptions.

In modern Android development, the industry consensus is to **eliminate BaseFragment and BaseActivity entirely**. Shared behaviors are extracted into standalone, self-contained delegates implementing `DefaultLifecycleObserver` or composed via Jetpack Compose's `Scaffold(topBar = { ... })` where the toolbar parameter is naturally optional.


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
