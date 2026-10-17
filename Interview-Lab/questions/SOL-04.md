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

## Concept and technical explanation

The Liskov Substitution Principle (LSP), formulated by Barbara Liskov, asserts that subtypes must be completely substitutable for their base types without altering the correctness, invariants, or expected behaviors of the host program. Formally, behavioral subtyping mandates that preconditions cannot be strengthened in a subtype, postconditions cannot be weakened, and history constraints must be preserved. In Android engineering, LSP violations frequently manifest when subclasses throw UnsupportedOperationException, return arbitrary nulls to bypass inherited contracts, or silently no-op inherited lifecycle methods in bloated base classes (such as BaseFragment or BaseAdapter).

## Practical walkthrough (English)

Contrasting an LSP violation with behavioral subtyping in an Android Repository:
```kotlin
// BAD ANTI-PATTERN: Violates LSP (Subtype breaks base contract by throwing UnsupportedOperationException)
interface CacheableRepository<T> {
    suspend fun get(): T
    suspend fun save(item: T) // Base contract implies all implementations can save!
}

class ReadOnlyRemoteRepository : CacheableRepository<UserConfig> {
    override suspend fun get(): UserConfig = fetchFromRemote()
    override suspend fun save(item: UserConfig) {
        // Blatant LSP Violation! Calling code expecting CacheableRepository crashes at runtime!
        throw UnsupportedOperationException("Read-only repository cannot save data")
    }
}

// ARCHITECTURAL BEST PRACTICE: Segregated contracts adhering to Liskov Substitution
interface ReadableDataSource<T> { suspend fun get(): T }
interface WritableDataSource<T> { suspend fun save(item: T) }

// Fully substitutable readable repository
class ReadOnlyRemoteConfig(private val api: ConfigApi) : ReadableDataSource<UserConfig> {
    override suspend fun get(): UserConfig = api.fetchConfig()
}

// Fully substitutable read-write repository
class LocalDiskCache(private val dao: ConfigDao) : ReadableDataSource<UserConfig>, WritableDataSource<UserConfig> {
    override suspend fun get(): UserConfig = dao.getConfig()
    override suspend fun save(item: UserConfig) = dao.insertConfig(item)
}
```

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

The Liskov Substitution Principle asserts that any subtype must be completely substitutable for its parent type without breaking application correctness. In Android, violating LSP commonly occurs when a subclass throws UnsupportedOperationException or returns unexpected nulls to avoid executing an inherited method. We adhere to LSP by keeping base interfaces focused, honoring all inherited behavioral contracts, and preferring fine-grained composition over deep inheritance hierarchies.

## Interview answer — structured

The Liskov Substitution Principle ensures that inheritance hierarchies represent genuine behavioral compatibility rather than superficial code reuse.
LSP goes beyond syntactic type matching to enforce behavioral contracts. If class B extends class A, any component designed to operate on an instance of A must function correctly when given an instance of B, without requiring runtime type inspections like instanceof or is checks.
In Android development, LSP is routinely violated in data persistence and base UI hierarchies. A notorious example is defining a general-purpose repository interface with both read and write methods, and then implementing a read-only variant that throws UnsupportedOperationException inside the write method. When background sync workers or UseCases invoke the write method expecting normal execution, the application crashes with an unexpected runtime exception.
Another frequent violation occurs in UI code with bloated BaseFragment or BaseActivity classes that mandate methods like setupToolbar() or enableSwipeRefresh(). When a child screen without a toolbar overrides the method with an empty body, it breaks caller invariants and creates subtle rendering bugs.
To uphold LSP, engineers replace monolithic inheritance hierarchies with fine-grained interfaces. By splitting contracts into distinct Readable and Writable interfaces, every implementing class satisfies its entire contract unconditionally.

## Interview answer — deep senior

Under the hood, the Liskov Substitution Principle is formalized through Design by Contract: a subtype may weaken preconditions (demand less) and strengthen postconditions (guarantee more), but never the reverse.
In Android runtime execution, violating LSP introduces insidious failure modes that evade compile-time detection. When a subclass strengthens a precondition by requiring non-null arguments where the base contract permitted nullable parameters, or when a subclass weakens postconditions by returning an uninitialized state machine, callers relying on polymorphism execute incorrect branch paths.
A classic Android framework violation occurred in Java collections, where Collections.unmodifiableList() implemented java.util.List but threw UnsupportedOperationException on add(). If an Android engineer passes an unmodifiable list to an adapter expecting a mutable list, crashes occur at runtime.
Staff engineers eliminate these risks in modern Kotlin through type-system design and immutable data modeling. Kotlin explicitly separates List (read-only interface) from MutableList (read-write interface), baking LSP compliance directly into the language standard library.
Furthermore, in modern Jetpack Compose architectures, LSP violations are systematically eradicated because Compose completely abandons deep class inheritance in favor of pure function composition, immutable state data classes, and Modifier chaining, rendering classical inheritance substitute bugs obsolete across all UI presentation layers. By enforcing contract invariants through explicit interfaces, runtime regressions are caught at compile time rather than crashing user devices in production.

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
