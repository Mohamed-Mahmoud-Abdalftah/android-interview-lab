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

لو `BaseFragment` بتطلب `setupToolbar()` وكل child لازم تنفذها، screen من غير toolbar هتعمل no-op أو ترمي exception. لو base contract وعد إن كل Fragment عندها toolbar قابل للإعداد، subclass دي ما تقدرش تحل محل base من غير special case، وده LSP violation. لو method optional بوضوح وdefault no-op والcallers مش بتفترض toolbar، قد لا يكون violation تقني، لكنه design smell. الأفضل `ToolbarOwner` capability أو `ToolbarController` collaborator للشاشات اللي تحتاجها، وما تحطش واجهة UI ثابتة في كل Fragment.

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

## Practical walkthrough

السؤال هنا مش إن `setupToolbar()` فاضية وخلاص؛ هل base contract بيقول إن كل Fragment يقدر يجهز toolbar؟ لو camera screen مفيهاش toolbar وبتعمل throw أو no-op مخفي، caller بيتعامل معاها كبديل وبيفشل. الأفضل تخلي capability مستقلة `ToolbarHost` أو controller يتضاف للشاشات المناسبة فقط. لو method optional صراحة وبلا افتراض من callers، LSP قد لا تنكسر لكن تصميم الـbase غالبًا لسه مربك. اختبر caller كان بيعمل إيه مع أي subclass، خصوصًا بعد navigation أو recreation.

## Trade-offs and decision criteria

A default no-op can be acceptable if optional behavior is explicit and callers do not rely on it. A capability interface adds wiring but prevents invalid base assumptions. Avoid adding an interface if a simple local helper suffices.

## Failure modes

A subclass throws `UnsupportedOperationException` from `setupToolbar`, so a base lifecycle callback crashes on that screen. Replace mandatory hook and migrate toolbar screens behind an explicit capability; test both toolbar and no-toolbar navigation.

## Production perspective

A media app has camera and library Fragments. Only library screens compose a toolbar controller; camera screen stays immersive. Shared analytics remains a separate lifecycle-aware collaborator rather than a BaseFragment field.

## Interview answer — short

It violates LSP when the base contract promises toolbar setup but a subclass cannot support it and must throw or break caller expectations. I would narrow the capability or use composition. A documented optional no-op is a different contract.

## Interview answer — structured

I first ask what `BaseFragment` promises. If callers can treat every subclass as toolbar-capable, a screen that throws from `setupToolbar()` breaks substitution. A no-op may also be misleading if callers expect visible configuration. I would extract a `ToolbarHost` or controller used only by toolbar screens and remove the requirement from the common base. If the hook is explicitly optional with no caller guarantee, it may not be a strict LSP violation, though the hierarchy may still be awkward. In a migration, I would preserve screens that actually use the toolbar while removing the compulsory hook from screens that do not. I would test rotation and back navigation because toolbar setup often interacts with the Activity lifecycle.

## Interview answer — deep senior

The principle is behavioral, not syntax-based. A subclass can compile while rejecting a valid operation of its base type. If `BaseFragment` always calls `setupToolbar()` during lifecycle and one child has no toolbar, throwing is a clear failure. A silent no-op may also violate user-visible expectations depending on the documented contract. I would add tests that exercise the base behavior through each subclass, then introduce an explicit toolbar capability for only the applicable screens. The migration can be incremental: stop invoking the hook unconditionally, move toolbar setup to a collaborator, and remove obsolete overrides. I would also inspect other BaseFragment responsibilities such as analytics and permissions, because the same overbroad abstraction often hides lifecycle leaks and test coupling. I would ask what callers are promised by `BaseFragment`. If the base says every screen can configure a toolbar, a camera subclass that throws or silently does nothing breaks substitutability when a caller invokes that behavior. The fix is to move the capability to a narrow `ToolbarHost` or compose a controller only into screens with toolbars. If the base explicitly models optional toolbar behavior and callers handle absence, the LSP claim is less direct, though the hierarchy may still be awkward. I would migrate call sites to depend on the capability they actually require and test navigation and recreation, where hidden no-op behavior often surfaces.

## How to answer in the interview

- **Why:** State the promised base behavior.
- **How:** explain substitution at caller site.
- **Trade-offs:** mention optional-contract nuance.
- **Failure cases:** show throw/no-op failure.
- **Production solutions:** propose explicit capability and caller tests..

## Deep-dive talking points

State base contract precisely, distinguish no-op from throw, and outline a safe capability extraction.

## Follow-up questions

- [SOL-04](../sol-04/): What does LSP require? **Answer:** subclasses honor the behavior clients expect from the base.
- [SOL-11](../sol-11/): How replace the giant base? **Answer:** compose optional lifecycle-aware collaborators.

## Self-check rubric

Explain the contract condition for violation, give a counterexample where optional no-op is legal, and propose a refactor.

## References and reviewed-on date

- [Kotlin inheritance](https://kotlinlang.org/docs/inheritance.html) — override behavior.
- [Liskov and Wing, A Behavioral Notion of Subtyping](https://www.cs.columbia.edu/~wing/publications/LiskovWing94.pdf) — substitutability.

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.
