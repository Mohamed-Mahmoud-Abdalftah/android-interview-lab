---
id: "SOL-04"
question: "Explain Liskov Substitution Principle with an Android example."
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "A"
phase: 2
priority: "P1"
order: 175
editorial_status: "reviewed"
---

# SOL-04

## Original interview question

Explain Liskov Substitution Principle with an Android example.

## What the interviewer evaluates

Test behavioral substitutability, including preconditions, postconditions and failure semantics.

## Explanation in Arabic

شرح مبدأ استبدال لسكوف (Liskov Substitution Principle - LSP) مع مثال عملي واقعي في Android:

1. تعريف مبدأ لسكوف (LSP):
   - ينص المبدأ على: **"إذا كان الكائن S كلاس فرعي من T، فيجب أن يكون من الممكن استبدال كائنات T بكائنات S دون كسر صحة وسلوك البرنامج أو تغيير خصائصه المرغوبة"**.
   - الكلاس الفرعي يجب ألا يكسر الوعود والتوقعات (Contracts) التي قطعها الكلاس الأساسي.

2. ما الذي ينتهك LSP في Android؟
   - **رمي استثناءات غير متوقعة (UnsupportedOperationException)**: مثل كلاس `BaseFragment` يجبر جميع الشاشات على تنفيذ `setupToolbar()`، ولكن هناك شاشة شريط سفلي (Bottom Sheet) لا تمتلك Toolbar، فيقوم المطور بـ `override fun setupToolbar() { throw UnsupportedOperationException() }` أو تركها فارغة!
   - **تعديل الشروط المسبقة أو اللاحقة (Preconditions & Postconditions)**: كلاس أساسي يقبل أرقام سالبة، وكلاس فرعي يرمي Crash إذا كان الرقم سالباً.

3. كيف نطبق LSP بشكل سليم في Android؟
   - **استبدال الوراثة بالتركيب (Composition over Inheritance)**: بدلاً من فرض كل شيء في كلاس `BaseActivity` أو `BaseFragment` ضخم، نستخدم Component مستقلة أو Lifecycle Delegates، أو تقسيم الواجهات إلى عقود صغيرة.

## Practical walkthrough

المقارنة بين انتهاك LSP في كلاسات الـ Base وكود متوافق مع LSP عبر الـ Delegates:
```kotlin
// ❌ انتهاك صارخ لـ LSP: إجبار الكلاس الفرعي على سلوك لا يدعمه مما يكسر التوقعات:
open class BaseFragment : Fragment() {
    open fun setupToolbar() {
        // يتوقع الكود أن كل Fragment يمتلك Toolbar صالحاً للربط
    }
}

class FullScreenVideoFragment : BaseFragment() {
    override fun setupToolbar() {
        // 💥 يكسر LSP: يرمي استثناء أو يتجاهل العقد لأن شاشة الفيديو بدون Toolbar!
        throw UnsupportedOperationException("Video screen does not have a toolbar")
    }
}

// ✅ تطبيق LSP السليم: فصل السلوك الاختياري في واجهة أو Delegate مستقل:
interface ToolbarConfigurable {
    fun configureToolbar(toolbar: Toolbar)
}

class HomeFragment : Fragment(), ToolbarConfigurable {
    override fun configureToolbar(toolbar: Toolbar) { /* إعداد Toolbar للشاشات التي تحتاجه فقط */ }
}

class VideoFragment : Fragment() {
    // لا ينفذ ToolbarConfigurable؛ لا استثناءات غير متوقعة ولا كسر للعقود!
}
```

## Why it matters and how it works

Subtyping is a behavioral promise. Clients rely on documented preconditions, outcomes, side effects and lifetime. A subclass that rejects valid base calls or silently weakens results breaks that promise even if signatures match.

## Worked example

Illustrative contract: `interface ThumbnailLoader { suspend fun load(uri: Uri): Bitmap? }`. An implementation that throws for all remote URIs violates the contract if remote URIs were promised. Either narrow the contract to supported schemes or provide separate capabilities. This is conceptual Android code; imports and permission/lifecycle details are intentionally omitted.

## Trade-offs and decision criteria

Inheritance is useful when all subtypes truly share behavior and invariants. Composition or small capability interfaces are safer when implementations differ fundamentally. Overly strict contracts can exclude useful implementations, so document supported inputs explicitly.

## Failure modes

`OfflineImageLoader` overrides `load` and throws for every HTTP URI accepted by the base contract; callers now need subtype checks, showing substitution failed. Fix the contract or use a separate loader strategy with declared capabilities.

## Production perspective

An SDK adapter contract defines success, failure, cancellation and timeout behavior. Contract tests run against each vendor implementation to ensure callers can swap providers without hidden special cases.

## Interview answer — short

Liskov Substitution Principle states that subclasses must be substitutable for their base classes without breaking program correctness. In Android, violating LSP manifests as throwing `UnsupportedOperationException` in subclasses (e.g. `BaseFragment.setupToolbar()`). We solve this by favoring composition or fine-grained interfaces over fat base classes.

## Interview answer — structured

The Liskov Substitution Principle (LSP), formulated by Barbara Liskov, requires that **subtypes must be completely substitutable for their base types without altering program correctness**.

A subclass must adhere strictly to the behavioral contract established by its superclass. Specifically.

First, a Preconditions cannot be strengthened is a subclass cannot demand stricter validation inputs than its parent. Next, a Postconditions cannot be weakened is a subclass cannot return less or fail to fulfill state guarantees made by the parent.
Finally, with Invariants must be preserved, any rules that hold true for the superclass must hold true for all subclasses.

In Android, the most pervasive LSP violation is the bloated **`BaseFragment` / `BaseActivity` anti-pattern**. A `BaseFragment` declares abstract methods like `setupToolbar()`, `enableSwipeToRefresh()`, and `getBottomNavIndex()`.
When a developer creates a fullscreen modal or onboarding slide that lacks a toolbar, they either override the method with an empty no-op or throw `UnsupportedOperationException("Not supported")`. Calling code expecting a valid toolbar crashes or behaves unpredictably.


## Interview answer — deep senior

The architectural remedy for LSP violations in Android is **Composition over Inheritance**.

Instead of forcing every screen to inherit from an arbitrary 800-line `BaseFragment`, we extract modular capabilities into dedicated lifecycle-aware delegates.

First, a `ToolbarDelegate` that attaches to screens that explicitly implement `ToolbarConfigurable`. Finally, a `NetworkStateDelegate` that observes connectivity.

In Jetpack Compose, LSP violations are naturally minimized because Compose entirely abandons inheritance hierarchies. A composable screen does not inherit from `BaseScreen`; instead, screens compose reusable composable decorators (`Scaffold`, `TopAppBar`, `PullToRefreshBox`) purely through function composition.


## How to answer in the interview

- **Why:** State the behavioral promise.
- **How:** test both implementations with the same cases.
- **Trade-offs:** discuss narrower contracts.
- **Failure cases:** show the throwing subtype.
- **Production solutions:** finish with contract tests including Android failures..

## Deep-dive talking points

Discuss behavioral contracts beyond signatures, strengthened preconditions, weakened postconditions and contract-test suites.

## Follow-up questions

- **Interviewer:** "Why is throwing `UnsupportedOperationException` a classic sign of an LSP violation?"
  **Answer:** "Because the base class promised that the operation could be invoked. Throwing an exception unexpectedly breaks the caller's reasonable expectations."

- **Interviewer:** "How does Jetpack Compose naturally eliminate LSP violations in UI?"
  **Answer:** "Compose uses functional composition instead of OOP inheritance hierarchies. UI components don't subclass `View` or `Activity`; they are pure functions that accept parameters."

## Self-check rubric

State one behavioral promise, one violating subclass, and a contract test or interface split.

## References and reviewed-on date

- [Liskov and Wing, A Behavioral Notion of Subtyping](https://www.cs.columbia.edu/~wing/publications/LiskovWing94.pdf) — behavioral substitution; hosted academic copy.
- [Kotlin inheritance](https://kotlinlang.org/docs/inheritance.html) — language mechanics only.

Technically reviewed against primary documentation on 2026-10-13.
