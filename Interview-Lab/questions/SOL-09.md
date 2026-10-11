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

Composition over inheritance يعني تبني behavior من objects صغيرة متعاونة بدل BaseActivity أو BaseFragment ضخمة تورّثها لكل screen. في Kotlin، constructor injection وdelegation يخلّوا logging، permission handling، navigation helpers عقود واضحة؛ كل screen تختار اللي تحتاجه. inheritance تربط subclass بprotected lifecycle hooks وفرضيات base، وتعديل base ممكن يكسر كل الشاشات. لكنها مفيدة لو عندك true is-a contract ثابت مثل specialized View أو framework base مطلوب. المهم ما تورّثش عشان تشارك helper function فقط.

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

Composition builds behavior from collaborators, while inheritance binds a subtype to a base contract and implementation. I favor composition for optional Android behaviors so screens do not inherit methods they cannot honor.

## Interview answer — structured

A `BaseFragment` that forces every screen to have a toolbar creates a brittle hierarchy. With composition, a screen receives a toolbar controller only if it has one, and analytics or navigation can be separate collaborators. That reduces hidden lifecycle coupling and makes tests replace dependencies independently. Inheritance still makes sense when the subtype truly satisfies the base contract and shared behavior is stable. I choose by substitutability and ownership, not a rule that inheritance is always wrong. A concrete example is a screen without a toolbar. It should not inherit a base hook that it must override to do nothing or throw. It can simply omit a toolbar collaborator while still using analytics and navigation objects with lifetimes appropriate to that screen.

## Interview answer — deep senior

The risk in inheritance is that subclasses depend on implementation details and lifecycle assumptions of the base class. A change to `BaseActivity` may affect many screens, and children may add no-op or throwing overrides for behavior they do not support—an LSP smell. Composition lets each screen assemble only needed capabilities with explicit constructors or delegation. It also clarifies scopes: a navigation helper may be Activity-scoped while a payment SDK adapter belongs elsewhere. The cost is some wiring and interfaces where variation is real. I would keep framework inheritance where required and small true subtype hierarchies where contracts hold, but avoid using inheritance solely to share utility methods or global mutable state. I would check whether the base class provides a real is-a relationship or merely a bag of convenience methods. Inheritance exposes protected state and lifecycle hooks to every child, so a change in base can ripple widely. Composition makes dependencies visible and lets tests replace them independently, but it can overdo wiring if every tiny helper becomes an interface. Kotlin’s final-by-default classes support deliberate extension. I keep framework-required inheritance, use delegation where forwarding is appropriate, and prefer small collaborators for optional behaviors. Contract tests protect any true subtype hierarchy.

## Deep-dive talking points

Compare BaseFragment hooks with injected capabilities; discuss LSP, lifecycle ownership and Kotlin final-by-default classes.

## Follow-up questions

- [SOL-10](../sol-10/): Why is a mandatory toolbar hook risky? **Answer:** some child screens cannot honor the base behavior.
- [KOT-15](../kot-15/): What Kotlin feature helps composition? **Answer:** interface delegation can forward behavior to a collaborator.

## Self-check rubric

Redesign one bloated base class with two collaborators and state one valid inheritance case.

## References and reviewed-on date

- [Kotlin inheritance](https://kotlinlang.org/docs/inheritance.html) — explicit inheritance mechanics.
- [Kotlin delegation](https://kotlinlang.org/docs/delegation.html) — composition through forwarding.

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-11. Conceptual examples are not device-tested.
